// Extract public Go API from a package directory, emitting the common JSON
// schema on stdout. See the generator's README for the schema.
package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"go/ast"
	"go/parser"
	"go/printer"
	"go/token"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"unicode"
)

type Symbol struct {
	Name      string `json:"name"`
	Kind      string `json:"kind"`
	Receiver  string `json:"receiver,omitempty"`
	Signature string `json:"signature"`
	Doc       string `json:"doc"`
	File      string `json:"file"`
	Line      int    `json:"line"`
}

type Output struct {
	Binding string   `json:"binding"`
	Symbols []Symbol `json:"symbols"`
}

func isExported(name string) bool {
	if name == "" {
		return false
	}
	return unicode.IsUpper(rune(name[0]))
}

// receiverName returns the base type name of a receiver, stripping pointer
// and type-parameter decorations.
func receiverName(recv *ast.FieldList) string {
	if recv == nil || len(recv.List) == 0 {
		return ""
	}
	t := recv.List[0].Type
	for {
		switch n := t.(type) {
		case *ast.StarExpr:
			t = n.X
		case *ast.IndexExpr:
			t = n.X
		case *ast.IndexListExpr:
			t = n.X
		case *ast.Ident:
			return n.Name
		default:
			return ""
		}
	}
}

// printNode returns a formatted representation of an AST node. It is used
// to reconstruct signatures so that their formatting is normalised across
// source files.
func printNode(fset *token.FileSet, node ast.Node) string {
	var buf bytes.Buffer
	cfg := printer.Config{Mode: printer.UseSpaces | printer.TabIndent, Tabwidth: 4}
	if err := cfg.Fprint(&buf, fset, node); err != nil {
		return fmt.Sprintf("/* print error: %v */", err)
	}
	return buf.String()
}

func funcSignature(fset *token.FileSet, fd *ast.FuncDecl) string {
	// Shallow-copy the decl and strip both the Body and Doc so that printer
	// emits only the signature line without the preceding doc comment.
	shallow := *fd
	shallow.Body = nil
	shallow.Doc = nil
	s := printNode(fset, &shallow)
	return strings.TrimRight(s, " \t\n")
}

func genDeclSignature(fset *token.FileSet, gd *ast.GenDecl, spec ast.Spec) string {
	// Emit "<keyword> <spec>" for a single spec.
	var kw string
	switch gd.Tok {
	case token.TYPE:
		kw = "type"
	case token.VAR:
		kw = "var"
	case token.CONST:
		kw = "const"
	default:
		kw = gd.Tok.String()
	}
	specText := printNode(fset, spec)
	return kw + " " + strings.TrimRight(specText, " \t\n")
}

func docText(cg *ast.CommentGroup) string {
	if cg == nil {
		return ""
	}
	return strings.TrimRight(cg.Text(), "\n")
}

func walk(srcdir string) ([]Symbol, error) {
	var out []Symbol
	fset := token.NewFileSet()

	var files []string
	err := filepath.Walk(srcdir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if info.IsDir() {
			return nil
		}
		if !strings.HasSuffix(path, ".go") {
			return nil
		}
		if strings.HasSuffix(path, "_test.go") {
			return nil
		}
		files = append(files, path)
		return nil
	})
	if err != nil {
		return nil, err
	}
	sort.Strings(files)

	for _, path := range files {
		rel, err := filepath.Rel(srcdir, path)
		if err != nil {
			rel = path
		}
		f, err := parser.ParseFile(fset, path, nil, parser.ParseComments)
		if err != nil {
			fmt.Fprintf(os.Stderr, "warning: cannot parse %s: %v\n", path, err)
			continue
		}
		for _, decl := range f.Decls {
			switch d := decl.(type) {
			case *ast.FuncDecl:
				if !isExported(d.Name.Name) {
					continue
				}
				recv := receiverName(d.Recv)
				kind := "function"
				if recv != "" {
					kind = "method"
				}
				out = append(out, Symbol{
					Name:      d.Name.Name,
					Kind:      kind,
					Receiver:  recv,
					Signature: funcSignature(fset, d),
					Doc:       docText(d.Doc),
					File:      rel,
					Line:      fset.Position(d.Pos()).Line,
				})
			case *ast.GenDecl:
				for _, spec := range d.Specs {
					switch s := spec.(type) {
					case *ast.TypeSpec:
						if !isExported(s.Name.Name) {
							continue
						}
						kind := "type"
						if _, ok := s.Type.(*ast.StructType); ok {
							kind = "struct"
						} else if _, ok := s.Type.(*ast.InterfaceType); ok {
							kind = "interface"
						}
						doc := docText(s.Doc)
						if doc == "" {
							doc = docText(d.Doc)
						}
						out = append(out, Symbol{
							Name:      s.Name.Name,
							Kind:      kind,
							Signature: genDeclSignature(fset, d, s),
							Doc:       doc,
							File:      rel,
							Line:      fset.Position(s.Pos()).Line,
						})
					case *ast.ValueSpec:
						for i, name := range s.Names {
							if !isExported(name.Name) {
								continue
							}
							kind := "var"
							if d.Tok == token.CONST {
								kind = "const"
							}
							// Reconstruct "<kw> Name = value" per-name for clarity.
							var sig string
							var valExpr ast.Expr
							if i < len(s.Values) {
								valExpr = s.Values[i]
							}
							if valExpr != nil {
								sig = fmt.Sprintf("%s %s = %s", tokenKeyword(d.Tok), name.Name, printNode(fset, valExpr))
							} else if s.Type != nil {
								sig = fmt.Sprintf("%s %s %s", tokenKeyword(d.Tok), name.Name, printNode(fset, s.Type))
							} else {
								sig = fmt.Sprintf("%s %s", tokenKeyword(d.Tok), name.Name)
							}
							doc := docText(s.Doc)
							if doc == "" {
								doc = docText(d.Doc)
							}
							out = append(out, Symbol{
								Name:      name.Name,
								Kind:      kind,
								Signature: sig,
								Doc:       doc,
								File:      rel,
								Line:      fset.Position(name.Pos()).Line,
							})
						}
					}
				}
			}
		}
	}
	return out, nil
}

func tokenKeyword(t token.Token) string {
	switch t {
	case token.CONST:
		return "const"
	case token.VAR:
		return "var"
	}
	return t.String()
}

func main() {
	if len(os.Args) != 2 {
		fmt.Fprintln(os.Stderr, "usage: extract-go <srcdir>")
		os.Exit(2)
	}
	srcdir := os.Args[1]
	info, err := os.Stat(srcdir)
	if err != nil || !info.IsDir() {
		fmt.Fprintf(os.Stderr, "error: %s is not a directory\n", srcdir)
		os.Exit(2)
	}
	syms, err := walk(srcdir)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error: %v\n", err)
		os.Exit(1)
	}
	out := Output{Binding: "go", Symbols: syms}
	enc := json.NewEncoder(os.Stdout)
	enc.SetIndent("", "  ")
	if err := enc.Encode(out); err != nil {
		fmt.Fprintf(os.Stderr, "error: %v\n", err)
		os.Exit(1)
	}
}
