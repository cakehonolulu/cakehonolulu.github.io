+++
title = "🚧 [0x02] Crypto: Jumping the fence"
description = "Writeup for the third 2022's Advent of Hack CTF challenge"
date = "2022-04-29"
aliases = ["writeup", "writeups", "ctf", "ctfs"]
author = "cakehonolulu"
+++

1.- Provided challenge description
<br>

Can you find the encrypted code? Maybe is not as easy at is seems...

2.- Provided information
<br>

<code>
Lb't'cnga(lrgíñmranaitoran
amlIleyelneudarFmaBeoDinSraiaaoaiBroamsrc,er,oiBroa
saa,leoWlaaolSaaiiacn)niagMn,emcñ(cl)aiaaíaosñt(cl)
rsmudradlraknitioeMtSdeae
</code>

3.- Challenge


This challenge is an interesting one, it tests your crypto-detection capabilities (And your ability to search in strange places for hints...)


While you could go ahead and decrypt the message, you'd still be missing the hint that enables you to solve the challenge...

If you view the source code of the challenge's website you find a hint hidden in a HTML comment:

<code>The code is the next 12 words of the song without spaces, jumps, comas and dots


So next, I inspected the provided code... Immediately found the use of Spanish glyphs (ñ), so that led me to know that the song was spanish... in a way...

The code can be decrypted using a zig-zag cypher solver (4 rows, 9 offset)

Decrypting it gives us:

<code>Lasramblas,I'llmeetyouWe'lldancearoundlaSagradaFamilia(Barcelona)DrinkingSangríaMiniña,teamomicariño(Barcelona)MamasitaricaSí,teadoro,señorita(Barcelona)</code>

Which is the lyrics of an Ed Sheeran song related to Barcelona...

So we search up the song's lyrics to find the next 12 words and...
<br>

<code>Advent{LosotrosvivalavidaComeonlet'sbefreeinBarcelona}</code>
