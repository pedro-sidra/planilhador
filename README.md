# planilhador
Auto-fills my personal finance excel sheets using the nubank API


## Install
Install the repo (optionally in a venv) with:
```
# (optional)
python3 -m venv myenv
source myenv/bin/activate

# Install
python3 -m pip install requirements.txt
```

If you are in a linux machine and want to use the `install.sh` util to send emails, install mutt: 

```
sudo apt-get install mutt
```

## Configure
After installation, there are some things to configure.

* First of all, navigate to this repo`s folder, e.g.:

```
cd /path/to/planilhador
```

* Add users of the system. The following script will guide you through the process:
    ```
    python3 add_user.py
    ```
   
**(for linux machines:)**
* Configure log folders and create `job.sh`:
    ```
    bash install.sh
    ```
* Edit the ~/.muttrc file with your email credentials. If you use gmail, follow [this tutorial](https://linuxconfig.org/how-to-install-configure-and-use-mutt-with-a-gmail-account-on-linux)
* Configure crontab to run `job.sh` daily:
    ```
    crontab -e
    ```
    and insert the following line at the end of the file, replacing /path/to/planilhador with the correct path to this repo:
    ```
    0 0 * * * /path/to/planilhador/job.sh
    ```
    (runs job.sh every day at midnight)

**(for windows machines:)**
I don't know how to schedule and send emails automatically in windows, but you can update your sheets manually with:
```
python3 job.py
```