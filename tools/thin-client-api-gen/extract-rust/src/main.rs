//! Extract public Rust API from a crate's `src/` directory, emitting the
//! common JSON schema on stdout. Uses `syn` for AST parsing.

use serde::Serialize;
use std::env;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::ExitCode;
use syn::{Attribute, Expr, ImplItem, Item, Lit, Meta, Visibility};
use walkdir::WalkDir;

#[derive(Serialize)]
struct Symbol {
    name: String,
    kind: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    receiver: Option<String>,
    signature: String,
    doc: String,
    file: String,
    line: usize,
}

#[derive(Serialize)]
struct Output {
    binding: &'static str,
    symbols: Vec<Symbol>,
}

fn is_public(vis: &Visibility) -> bool {
    matches!(vis, Visibility::Public(_))
}

/// Collect all `///` doc comments into a single string.
fn extract_doc(attrs: &[Attribute]) -> String {
    let mut lines = Vec::new();
    for attr in attrs {
        if !attr.path().is_ident("doc") {
            continue;
        }
        if let Meta::NameValue(nv) = &attr.meta {
            if let Expr::Lit(expr_lit) = &nv.value {
                if let Lit::Str(s) = &expr_lit.lit {
                    let raw = s.value();
                    // Doc comment text from syn already has leading space stripped
                    // of the `///` delimiter but retains the first space after it;
                    // we normalise by stripping one leading space per line.
                    let normalised = raw.strip_prefix(' ').unwrap_or(&raw).to_string();
                    lines.push(normalised);
                }
            }
        }
    }
    lines.join("\n")
}

/// Pretty-print a `syn` item as a signature-only string (no body).
fn render_item(item: &Item) -> String {
    // Use prettyplease for clean formatting; for items with bodies we want
    // the bodies stripped so the emitted text is signature-only.
    match item {
        Item::Fn(f) => {
            let mut clone = f.clone();
            clone.block = syn::parse_quote!({});
            // Print as `syn::File` to get formatted output.
            let file = syn::File {
                shebang: None,
                attrs: Vec::new(),
                items: vec![Item::Fn(clone)],
            };
            let out = prettyplease::unparse(&file);
            strip_empty_body(out)
        }
        Item::Struct(_) | Item::Enum(_) | Item::Type(_) | Item::Const(_) | Item::Static(_) => {
            let file = syn::File {
                shebang: None,
                attrs: Vec::new(),
                items: vec![item.clone()],
            };
            prettyplease::unparse(&file).trim_end().to_string()
        }
        _ => String::new(),
    }
}

/// Pretty-print an `impl` block method (signature-only, no body).
fn render_impl_method(method: &syn::ImplItemFn) -> String {
    let mut clone = method.clone();
    clone.block = syn::parse_quote!({});
    // Wrap in a synthetic impl block for formatting context.
    let file = syn::File {
        shebang: None,
        attrs: Vec::new(),
        items: vec![Item::Fn(syn::ItemFn {
            attrs: Vec::new(),
            vis: clone.vis.clone(),
            sig: clone.sig.clone(),
            block: Box::new(clone.block.clone()),
        })],
    };
    strip_empty_body(prettyplease::unparse(&file))
}

/// Remove the trailing ` {}` inserted by `parse_quote!({})`.
fn strip_empty_body(mut s: String) -> String {
    // prettyplease renders `{}` either on the same line or next line.
    for pat in [" {}", " {\n}", " {\n    }"] {
        if let Some(idx) = s.rfind(pat) {
            if idx + pat.len() >= s.trim_end().len() {
                s.truncate(idx);
                return s.trim_end().to_string();
            }
        }
    }
    s.trim_end().to_string()
}

fn impl_target_name(ty: &syn::Type) -> Option<String> {
    if let syn::Type::Path(tp) = ty {
        tp.path.segments.last().map(|s| s.ident.to_string())
    } else {
        None
    }
}

fn process_file(path: &Path, srcroot: &Path, symbols: &mut Vec<Symbol>) {
    let Ok(source) = fs::read_to_string(path) else {
        eprintln!("warning: cannot read {}", path.display());
        return;
    };
    let Ok(file) = syn::parse_file(&source) else {
        eprintln!("warning: cannot parse {}", path.display());
        return;
    };

    let rel = path
        .strip_prefix(srcroot)
        .unwrap_or(path)
        .to_string_lossy()
        .to_string();

    for item in &file.items {
        match item {
            Item::Fn(f) if is_public(&f.vis) => {
                symbols.push(Symbol {
                    name: f.sig.ident.to_string(),
                    kind: "function".into(),
                    receiver: None,
                    signature: render_item(item),
                    doc: extract_doc(&f.attrs),
                    file: rel.clone(),
                    line: 0,
                });
            }
            Item::Struct(s) if is_public(&s.vis) => {
                symbols.push(Symbol {
                    name: s.ident.to_string(),
                    kind: "struct".into(),
                    receiver: None,
                    signature: render_item(item),
                    doc: extract_doc(&s.attrs),
                    file: rel.clone(),
                    line: 0,
                });
            }
            Item::Enum(e) if is_public(&e.vis) => {
                symbols.push(Symbol {
                    name: e.ident.to_string(),
                    kind: "enum".into(),
                    receiver: None,
                    signature: render_item(item),
                    doc: extract_doc(&e.attrs),
                    file: rel.clone(),
                    line: 0,
                });
                for v in &e.variants {
                    symbols.push(Symbol {
                        name: v.ident.to_string(),
                        kind: "enum_variant".into(),
                        receiver: Some(e.ident.to_string()),
                        signature: format!("{}::{}", e.ident, quote::quote!(#v)),
                        doc: extract_doc(&v.attrs),
                        file: rel.clone(),
                        line: 0,
                    });
                }
            }
            Item::Type(t) if is_public(&t.vis) => {
                symbols.push(Symbol {
                    name: t.ident.to_string(),
                    kind: "type".into(),
                    receiver: None,
                    signature: render_item(item),
                    doc: extract_doc(&t.attrs),
                    file: rel.clone(),
                    line: 0,
                });
            }
            Item::Const(c) if is_public(&c.vis) => {
                symbols.push(Symbol {
                    name: c.ident.to_string(),
                    kind: "const".into(),
                    receiver: None,
                    signature: render_item(item),
                    doc: extract_doc(&c.attrs),
                    file: rel.clone(),
                    line: 0,
                });
            }
            Item::Impl(imp) if imp.trait_.is_none() => {
                let Some(target) = impl_target_name(&imp.self_ty) else {
                    continue;
                };
                for impl_item in &imp.items {
                    if let ImplItem::Fn(m) = impl_item {
                        if !is_public(&m.vis) {
                            continue;
                        }
                        symbols.push(Symbol {
                            name: m.sig.ident.to_string(),
                            kind: "method".into(),
                            receiver: Some(target.clone()),
                            signature: render_impl_method(m),
                            doc: extract_doc(&m.attrs),
                            file: rel.clone(),
                            line: 0,
                        });
                    }
                }
            }
            _ => {}
        }
    }
}

fn main() -> ExitCode {
    let args: Vec<String> = env::args().collect();
    if args.len() != 2 {
        eprintln!("usage: extract-rust <srcdir>");
        return ExitCode::from(2);
    }
    let srcroot = PathBuf::from(&args[1]);
    if !srcroot.is_dir() {
        eprintln!("error: {} is not a directory", srcroot.display());
        return ExitCode::from(2);
    }

    let mut symbols = Vec::new();
    let mut rs_files: Vec<PathBuf> = WalkDir::new(&srcroot)
        .into_iter()
        .filter_map(Result::ok)
        .filter(|e| e.file_type().is_file())
        .map(|e| e.path().to_path_buf())
        .filter(|p| p.extension().map(|e| e == "rs").unwrap_or(false))
        .collect();
    rs_files.sort();

    for path in &rs_files {
        process_file(path, &srcroot, &mut symbols);
    }

    let out = Output {
        binding: "rust",
        symbols,
    };
    match serde_json::to_writer_pretty(std::io::stdout(), &out) {
        Ok(()) => {
            println!();
            ExitCode::SUCCESS
        }
        Err(e) => {
            eprintln!("error: {}", e);
            ExitCode::FAILURE
        }
    }
}
