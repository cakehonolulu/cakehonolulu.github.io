+++
title = "🍸 [0x01] Reverse engineering: Cocktail"
description = "Writeup for the second 2022's Advent of Hack CTF challenge"
date = "2022-04-29"
aliases = ["writeup", "writeups", "ctf", "ctfs"]
author = "cakehonolulu"
+++

1.- Provided challenge description
<br>

The code is inside this program, can you find it?

# 2.- Provided files
<br>
<h3 style="color:lightblue">

<a href="https://raw.githubusercontent.com/cakehonolulu/HackUPC/main/2022/AdventOfHackUPC/CKT/code.py">code.py</a>


# 3.- Challenge


This challenge tests your Python knowledge, so it's a good idea to have at least the bare minimum idea of how to write simple programs on it


We try to run the script (<code>python3 code.py</code>) and it errors out, by looking at the code we can see that it expects an argument
so we provide a random one to it, prints out "No"


By inspecting the code you can see that it does some Python String Slicings, so it should be as easy as reversing the algorithm used to craft the flag (The result gets compared to a string to know if that's the flag)

The main idea behind the algorithm is that it works kinda like a cocktail mixer, you pour some content from the left glass and then some from the right glass; generating an unique mixture crafted by both glasses (The flag)

While you can do the reversing manually, I personally wrote a script that crafted the flag automatically.

<code>Advent{NJgm4LQC6afk8MstzVuiFAtn21xpjAWq}</code>

