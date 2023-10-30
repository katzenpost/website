Katzenpost Website
==================

This repository contains the sources of the Katzenpost website

- https://katzenpost.network

*This is *not* the Katzenpost Documentation code you might be looking for...*


## Download

```
git clone https://github.com/katzenpost/website.git
cd website/
```

Developing or building the source code requires:

- [Hugo](https://gohugo.io) mininum version [v0.100.0 extended](https://github.com/gohugoio/hugo/releases/tag/v0.100.0)


## Develop

To build locally and watch for live changes, run:

```
cd website/
hugo server -w -v --buildFuture --buildDrafts
```


## Build

To build for deployment, run:

```
rm -rf /path/to/html/katzenpost.network/*
hugo -d /path/to/html/katzenpost.network/ --buildFuture
```
    

## License

The content of this repository except images is licensed under the [Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/).

![image](https://i.creativecommons.org/l/by-sa/4.0/88x31.png)
