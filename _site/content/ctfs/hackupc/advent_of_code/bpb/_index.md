+++
title = "🧩 [0x00] Binary problem: Byte per byte"
description = "Writeup for the first 2022's Advent of Hack CTF challenge"
date = "2022-04-29"
aliases = ["writeup", "writeups", "ctf", "ctfs"]
author = "cakehonolulu"
+++


# 1.- Provided challenge description

<br>

The code is inside the binary code of this binary following this structure: Advent{code}. Good luck!

# 2.- Provided files

<br>
<a href="https://github.com/cakehonolulu/HackUPC/blob/main/2022/AdventOfHackUPC/BPB/byte_per_byte?raw=true">byte_per_byte</a>


# 3.- Challenge

<br>

We'll apply the 'lowest hanging fruit' methodology, that is, testing each thing from the bottom up so that we don't
forget anything inbetween.

We run the <code>file</code> command to see what information we may get from the binary; it returns:

{{< highlight bash >}}
byte_per_byte: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2,
BuildID[sha1]=bfca996e2b11c48694a780ff141d9b4c5dc88fdc, for GNU/Linux 3.2.0, not stripped
{{< /highlight >}}


Binary isn't stripped (That means it has debug symbols which may come in handy if there's any need to disassemble the file), we'll run it to see how it behaves (<code>./byte_per_byte</code>):

All it does is print "Nothing to see here..." string on the screen

We run a quick hexdump on the file (<code>hexdump -c byte_per_byte</code>) and we discover the flag at offset 0x00003020 with 2 NULL bytes of padding inbetween ASCII characters, fixing the representation yields us the flag:

<code>Advent{qkGGTxcRmwfDQP8ZrJQuFPIm5Jyim3pn}</code>

