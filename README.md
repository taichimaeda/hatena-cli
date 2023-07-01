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
~$ python -m pip install hatena-cli
~$ pandoc --version
~$ hatena --version
```

Before you can dive into the functionality of `hatena-cli`, you need do a bit of setup. Just follow these steps:

```bash
~$ hatena config init
```

If you need more configurations, try these commands:

```bash
~$ hatena config list
~$ hatena config set pandoc:path /usr/local/pandoc
~$ hatena config get pandoc:path
```

Now, let's see `hatena-cli` in action! Check out these examples:

```bash
~$ hatena upload --with-images 'My First Blog' '~/Documents/first-blog.md'
~$ hatena update --with-images 'My First Blog 2' '~/Documents/first-blog2.md' 230805800
~$ hatena delete --with-images 230805800
```

`hatena upload` and `hatena delete` require the blog ID of your entry on Hatena Blog.

To find this blog ID, take a look at the URL of Hatena Blog's web editor. It's the `<blog_id>` part in this format:

`https://blog.hatena.ne.jp/<user>/<domain>/edit?entry=<blog_id>`

Remember, when you use the `--with-images` option with `hatena update`, it deletes all previously referenced images and uploads the new ones from your local Markdown file. It can take some time, so use it wisely. It might be quicker to use the web editor if the changes are small.

Happy blogging!
