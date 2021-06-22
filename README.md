# The-Leaders
Cloud Innovation Center at RMIT University. Team: The Leaders



**Problem Statement:**
	How can we increase the resilience of Australia’s democratic institutions in the face of this cyber enabled threat to our sovereignty by creating cyber awareness at workplaces?
 



**Solution:**
	The Cyber Safe Test (CST) ready to combat this challenge by raising cyber security awareness. CST will streamline the education process related to security tests. 
Phishing emails is the most common cyber-attack and will continue to be, unless something is done. With dynamic implementation of such phishing tests, a management team can enable employees to have a clear and intuitive understanding of cyber security awareness. 




**Features:**

   - Send a fake phishing email internally to a targetted team in a few seconds. 
   - Upload multiple email addresses at once and send the email to multiple teams
   - Visualize your team's performance via the dashboard



**Setup Steps**


- Install Python on your system.
- Check if pip is installed or not for your OS. If not install pip. Guidelines: https://ehmatthes.github.io/pcc/chapter_12/installing_pip.html
- Open the command prompt from the location of the downloaded code folder and run this command:
```
pip3 install -r requirments.txt.
```
This will install all the required libraries.
- In app.py, change varible names to the values and the account you want to configure as the account that will send and receive the emails.
- Next you will need to set up AWS SES and AWS SNS on the same email id as well.
- In the EmailList.csv, put the emails you want to send the phasing emails to. You will need to verify the sender and receiver of the emails once to set them up.
- Run the python app using the command:
```
python3 app.py
```
