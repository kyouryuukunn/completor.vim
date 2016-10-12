Completor
=========

Completor is an asynchronous code completion framework for vim8. New features
of vim8 are used to implement the fast completion engine with low overhead.
For using semantic completion, external completion tools should be installed.

Requirements
------------

* vim8,
* compiled with `python` or `python3`

Builtin Completers
------------------

* filename
* Rust. [racer](https://github.com/phildawes/racer#installation) should be installed.
* Python. [jedi](https://github.com/davidhalter/jedi#installation) should be installed.
* Javascript. Use [tern](http://ternjs.net) for completion.
* c/c++. Use clang for completions. `clang` should be installed.

Install
-------

* vim8 builtin package manager:

```bash
mkdir -p ~/.vim/pack/completor/start
cd ~/.vim/pack/completor/start
git clone https://github.com/maralla/completor.vim.git
```

* [vim-plug](https://github.com/junegunn/vim-plug)

```vim
Plug 'maralla/completor.vim'
```
