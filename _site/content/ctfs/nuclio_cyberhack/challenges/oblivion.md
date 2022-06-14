+++
title = "🌐 [0x01] Oblivion"
description = "Writeup for 'Oblivion'"
date = "2022-06-14"
aliases = ["writeup", "writeups", "ctf", "ctfs"]
author = "cakehonolulu"
+++
<br>

![Oblivion](/images/ctfs/nuclio_cyberhack/oblivion/oblivion.png)

<table>
<thead>
  <tr>
    <th>Difficulty</th>
    <td>Beginner</td>
  </tr>
</thead>
<tbody>
  <tr>
    <th>Points</th>
    <td>20</td>
  </tr>
  <tr>
    <th>Category</th>
    <td>Networking</td>
  </tr>
</tbody>
</table>

# Description
<br>
<img src="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/160/openmoji/292/flag-for-catalonia-esct_1f3f4-e0065-e0073-e0063-e0074-e007f.png" width="20px" height="20px" style="vertical-align: bottom;"> Com veureu, sembla que el grup d'atacants es diu Oblivion, però de l'executable no sabem res sobre què fa, ni per a què serveix...
Comenceu la vostra investigació i descobriu el que pugueu. El que ens interessa és on es connecta, si és que ho fa.
Aleshores, el token del joc serà l'adreça IP de destinació...
<br>
<br>
🇺🇸 As you can see, it looks like the group of attackers is named Oblivion, but we know nothing about the executable file nor what it does...
Start investigating and discover as much as you can. The crucial part is finding where it connects (If it does...)
The flag for this challenge will be the target IP of the program.
<br>

<h1>Solution walkthrough</h1>

We're presented with a downloadable file named 'malware' (How appropiate); we download it and we start by doing all the low-hanging-fruit stuff.

{{< highlight bash >}}
$ file malware
malware: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2,
BuildID[sha1]=ac40f3d3f795f9ee657f59a09fbedea23c4d7e25, for GNU/Linux 2.6.32, stripped
{{< /highlight >}}

The usual stuff, note that it's stripped so if we have to debug it; it'll be harder.

You can run <code>strings</code> but we warned that it's a 12.3MB file so it'll take quite an amount of space of your terminal.

If you run it, you'll probably find out that it's a Python-packaged ELF file.

My instinct kicked in and I started to search for Python decompilers.

That was an error, the solution is far more easier than that; anyways, I decompiled the ELF file and found out that the <code>.pyc</code> files were <code>Python 3.9 Bytecode</code> which can't be disassembled as of right now (10/07/2022) so I had to abandon that path.


I'm not sure that compiling it w/3.9 was made on pruppose (To make us not able to decompile it) but there goes that.

Anyways, I proceeded to run the program:

![Program](/images/ctfs/nuclio_cyberhack/oblivion/program.png)

Interesting... I tried <code>ltrace</code> but as soon as Python code is executed, it doesn't output anything meaningless so I followed another path.

The <code>netstat</code> command helps us identify the network connections, routing tables, interface statistics and more at the time of execution, let's use it and filter by 'malware' which is the name of the binary.

{{< highlight bash >}}
$ netstat --tcp -np | grep "malware"
(Not all processes could be identified, non-owned process info
 will not be shown, you would have to be root to see it all.)
tcp        0      0 192.168.1.136:54604     45.33.32.156:9929       ESTABLISHED 45512/./malware
{{< /highlight >}}

Flag: <code>45.33.32.156</code>
