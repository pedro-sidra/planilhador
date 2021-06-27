
dir=`pwd`
command="python3 ${dir}/job.py"
env="${dir}/myenv"
mkdir -p ${dir}/log

# executable
echo "#!`which bash`" > job.sh
echo "set -e" >> job.sh
chmod +x job.sh
# Activate env
echo "source ${env}/bin/activate" >> job.sh
# Run python
echo "${command} > ${dir}/log/last_log.txt" >> job.sh
# Build email from message of th day and last log
echo "cat ${dir}/log/motd.txt ${dir}/log/last_log.txt > ${dir}/log/email.txt" >> job.sh
# Send email
echo "cat ${dir}/log/email.txt | mutt -s \`date +'%m/%d'\` \`cat ${dir}/log/recipients.txt\`" >> job.sh
# Build continuous log
echo "cat ${dir}/log/log.txt ${dir}/log/last_log.txt > ${dir}/log/log.txt" >> job.sh

echo "Type email recipients delimited by ,"
read recipients
echo "$recipients" > ${dir}/log/recipients.txt

echo "OK. Opening vim to edit the email contents file..."
sleep 1
vim ${dir}/log/motd.txt
echo "Your emails will contain the message of the day followed by the script log"
