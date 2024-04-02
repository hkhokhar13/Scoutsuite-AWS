from genericpath import isfile
import os
import datetime
from re import sub 
import requests
import shutil
import subprocess
from ScoutSuite import __main__
from utilities import upload_results


class Scout(object):
    def __init__(self) -> None:
        self.AWS_ACCESS_ID=os.environ.get("AWS_ACCESS_KEY")
        self.AWS_SECRET_ACCESS_KEY=os.environ.get("AWS_SECRET_ACCESS_KEY")
        self.SLACK_TOKEN=os.environ.get("SLACK_TOKEN_SS")
        self.today=datetime.datetime.now().strftime("%d-%m-%y")
        self.path="/app/scripts/report/"

    def run_scan(self):
        cmd =f"scout aws --report-dir {self.path} --report-name {self.today}-scout-report --no-browser --access-key-id {self.AWS_ACCESS_ID} --secret-access-key {self.AWS_SECRET_ACCESS_KEY}"
        return_code= subprocess.call(cmd,shell=True)
        print(return_code,"Scout run finished !!!!")
        #if os.path.isfile(f"{self.path}/{self.today}-scout-report.html"):
        print("Uploading data to Slack and Dojo")
        self.result2slack()
        self.result2dojo()

        """  __main__.run(
            provider="aws",
            access_key_id=self.AWS_ACCESS_ID,
            aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY,
            report_dir=self.path,
            report_name=f"{self.today}-scout-report",
            no_browser=True,
            result_format="json"
        ) """
        


    def result2slack(self):
        report_name=f"{self.today}-aws"
        report_path=f"/app/scripts/artifact/{report_name}"
        shutil.make_archive(report_path,"zip",self.path)
        with open(f"{report_path}.zip","rb") as f:
                report=f.read()
                f.close()
            
        header={"Authorization":"Bearer {}".format(self.SLACK_TOKEN)}
        param={
            "filename":"{}-aws.zip".format(self.today),
            "filetype":"zip",
            "initial_comment":"AWS Config Report",
            "channels":"C03CB550DRD",
            "title":"ScoutSuite Report"
        }
        file={"file": ("{}-aws.zip".format(self.today), report)}
        res=requests.post("https://slack.com/api/files.upload",data=param,files=file,headers=header)
        print(res.text)
    
    def result2dojo(self):

        status_code=upload_results("Scout Suite Scan",f"{self.path}/scoutsuite-results/scoutsuite_results_{self.today}-scout-report.js")
        if status_code== 201 :
            print("Successfully uploaded the results to Defect Dojo")
        else:
            print("Something went wrong, please debug " + str(status_code))

Scout().run_scan()
