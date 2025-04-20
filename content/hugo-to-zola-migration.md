+++
title = "Migrating my blog from Hugo to Zola"
date = 2025-04-20
description = "Or how I made my static-and-already-fast blog even faster (And safer!)"
[extra]
summary = "Why moving to Rust isn't as bad as it sounds, even for web."
author = "cakehonolulu"
[taxonomies]
tags = ["hugo", "golang", "zola", "rust"]
+++

## To blog or to not blog...

So... there's some point in time where you, as a software developer, you may face the urge to go on unedited rants regarding whatever project you
may be doing/participating.

Then you somehow think ("_The collective intellect that resteth in our mortal frames._", "_Our brain_" from now on)...

### Communication excerpt

**(Our brain)** - Hey, it could be cool to write and document for the posteriority whatever _niche_ thing we may be doing right now.

**(Ours)** - Hey, yeah! _Totally_. This is a cool way to preserve this (**Insert super esoteric tech fact/rant here**) for posteriority! You know, if, for some
unknown reason a future intelligent life (**Before humanity collapse or thereafter, provided somehow this piece of binary data ends up somewhere
accessible and hopefully in clear-text¹**) or maybe some random person over the internet finds this useful!

**(Our brain)** - Well, we _musteth_ find a way then...

_[¹] Sorry extra-terrestial beings! Hopefully you know the latin alphabet and it's basic meaning (Which I assume so proven you've gotten this far to get
ahold of this piece!)_

---

## Available technologies

You know, in a sea of technologies it's sometimes hard to try and choose... you could always...

You could always go ahead and make a frontend engine based on [ArnoldC](https://lhartikk.github.io/ArnoldC/) --

**my_coolblog.arnoldc:**
```nix
IT'S SHOWTIME
TALK TO THE HAND "hello blog"
TALK TO THE HAND "hasta la vista baby"
YOU HAVE BEEN TERMINATED
```

Kidding.... (_or not?_)

But yes, choosing what and how you want it to be tends to be increasingly difficult because for certain things you may want some features only available
in certain engines and some others not available... not to get started on where to host it.

Fortunately for me, I learned years ago about GitHub offering *.github.io subdomains "linked" to your username (There's probably a vastly more technical way of explaining
how this actually works in GitHub but this'll do for now) so I went down that route (Could be cool to have shadow copies on other code sharing services, or straight up
ditching this platform as a whole [due to an already long list of enshittification practises](https://sfconservancy.org/blog/2022/jun/30/give-up-github-launch/)) (You know
this may actually be the time to actually learn in a practical way about networking and whatnot by building a local homelab instead of those pesky long hours staring at
Wireshark dumps at university and self-host while I'm at it).

## With great power comes great responsibility

So, we got the "hosting" service... now we must choose something that fits our (My) needs. Again, we discussed this above but no, we're not doing it in ArnoldC (Or are we?) so
we'll have to settle for something more practical.

GitHub kinda limits you to have "static" HTML files. That is, there's many limits as what you can do; and before you ask, no, you can't have a pesky database on it or this cool flashy frontend/whatever the new coolest boy in the block is today, I should've added a disclaimer on the start of the entry in retrospective...

While there are a few candidates, Github's default one tends to be Jekyll if my memory serves me right; but it's not uncommon for users to ditch it altogether (You know, I kinda feel bad for the poor fellow that wanted to be the coolest one at Github by doing a static-site-generator using Ruby...) for another alternative.

That's what I personally did, and went with Hugo, which is written in Go and it's more tolerable for me.

## Oxidizing backend

It's not that I've never ever dealt with Rust, but the times I tried in the past (Pre-2025) have been fun but not heart-touching enough for me to justify switching my religious beliefs from C (More precisely, [HolyC](https://holyc-lang.com/)) (Before someone in the audience (_hello???_) asks, **yes** I was kidding) to it's _crusted_ counterpart.

That is, until some rainy day around January 2025 (Wasn't rainy but else it wouldn't have had the dramatic impact this has had, right? right...? oh no, I'm talking by myself again; sorry I must've forgotten my _Celexa_'s).

So I just kinda got this (un)necessary urge to Rust-ify myself. It's as closest to a spiritual awakening I'll probably ever get probably.

So there I went, looking for Rust alternatives for my programs (Shoutout to fish-shell for converting it's core engine to Rust!); and of course, converting some of mine to it.

I kinda started with the usuals, the projects you usually love more ([Neo2](https://github.com/cakehonolulu/Neo2) I love you but understand that [RustEE](https://github.com/cakehonolulu/RustEE) is the _cooler Daniel_ right now).

And then, I got a bit of an enlightment; what if there's a SSG made with Rust already?

It so does happen that there is, was going to ask for a slow drum roll but I kinda forgot I was alone here writing with a coffee and I'm not a percussionist so you'll have to imagine:

**[Zola](https://www.getzola.org/)**

So yeah, there it is. Considering you could also write the pages using Markdown (Well, actually a custom Markdown derivative that's also compatible with Markdown) I chose the first theme I could see and just used it, then it's been a matter of porting the general structure of the blog in Hugo here and ta-da!

Now we have a Rust-powered SSG for my blog.

I can also do cool math finally:

$$
 \varphi = 1+\frac{1} {1+\frac{1} {1+\frac{1} {1+\cdots} } }
$$

And cool diagrams:

{% mermaid() %}
graph TD
    A[(I start a blog)] --> B(I try not to forget about it)
    B --> C{I learn a new technology}
    C --> D[I write a new entry]
    C --> E[I implement the technology]
    E --> B
    D --> F[I try not to forget about it????]
    F --> B
{% end %}

So yeah, a lot of cool stuff, and it's super fast (And secure, _duh_!) (_Take that Meta!_)