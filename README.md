# `hatena-cli`

Command line utility for Hatena Blog.

`hatena-cli` is designed for Hatena Blog enthusiasts who perfer to keep their files stored locally on their machines.

Here's why `hatena-cli` is better than the traditional copy-paste approach:

1. No body length limits.

You know how Hatena Blog's web editor puts a cap on how much you can write? With `hatena-cli`, that's a thing of the past! You can upload massive Markdown files without any hassle.

2. Say goodbye to manual image uploads.

With the `--with-images` option, `hatena-cli` automatically sniffs out the local images referenced in your Markdown file and uploads them to your Hatena Fotolife storage. It even updates the image paths in the generated HTML file!

Currently, `hatena-cli` only supports Markdown files. But no worries, we're thinking about adding support for other file formats soon.

To get started, make sure you have `pandoc` and `hatena-cli` installed. You can install them by running these commands:

```bash
~$ brew install pandoc
...
~$ python -m pip install hatena-cli
...
~$ pandoc --version
pandoc 3.1.3
Features: +server +lua
Scripting engine: Lua 5.4
User data directory: /Users/taichimaeda/.local/share/pandoc
Copyright (C) 2006-2023 John MacFarlane. Web: https://pandoc.org
This is free software; see the source for copying conditions. There is no
warranty, not even for merchantability or fitness for a particular purpose.
~$ hatena --version
Hatena Blog CLI Version: 0.1.0
```

Before you can dive into the functionality of `hatena-cli`, you need do a bit of setup.

First, follow this tutorial to obtain your API key and secret:

https://developer.hatena.ne.jp/ja/documents/auth/apis/oauth/consumer

Then submit the details with `hatena config init`, after which you are ready to go!:

```bash
~$ hatena config init
hatena config init
auth:api_key: <api_key>
auth:api_secret: <api_secret>
blog:username: <user_id>
blog:domain: <user_id>.hatenablog.com
```

If you need more configurations, try these commands:

```bash
~$ hatena config list
List of config:
auth:api_key: <api_key>
auth:api_secret: <api_secret>
auth:access_token: 
auth:access_secret: 
auth:expires: 2023-07-02 12:00:00.000000
blog:username: <user_name>
blog:domain: <user_name>.hatenablog.com
image:pattern: src="(.+\.(?:jpg|png))"
image:replace: src="\1"
path:template: <home_dir>/Library/Application Support/hatena-cli/template.html
path:pandoc: /opt/homebrew/bin/pandoc
~$ hatena config set pandoc:path /usr/local/pandoc
path:pandoc: /usr/local/pandoc
~$ hatena config get pandoc:path
path:pandoc: /usr/local/pandoc
```

Now, let's see `hatena-cli` in action! Check out these examples:

```bash
~$ hatena upload --with-images 'My First Blog' ~/Documents/first-blog.md
...
~$ hatena update --with-images 'My First Blog 2' ~/Documents/first-blog2.md 820878482946714696
...
~$ hatena delete --with-images 820878482946714696
...
```

`hatena upload` and `hatena delete` require the blog ID of your entry on Hatena Blog.

To find this blog ID, take a look at the URL of Hatena Blog's web editor. It's the `<blog_id>` part in this format:

`https://blog.hatena.ne.jp/<user>/<domain>/edit?entry=<blog_id>`

On a first launch, you will be redirected to your web browser for authentication. Copy the code displayed and enter it when prompted.

Remember, when you use the `--with-images` option with `hatena update`, it deletes all previously referenced images and uploads the new ones from your local Markdown file. It can take some time, so use it wisely. It might be quicker to use the web editor if the changes are small.

Happy blogging!
