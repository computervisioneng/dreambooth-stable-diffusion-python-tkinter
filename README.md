# dreambooth-stable-diffusion-python-tkinter

<p align="center">
<a href="https://www.youtube.com/watch?v=">
    <img width="100%" src="https://utils-computervisiondeveloper.s3.amazonaws.com/thumbnails/train_dreambooth_python.jpg" alt="Watch the video">
</a>
</p>

## execution

### setup AWS

- Go to [AWS](https://aws.amazon.com/).
- Go to S3 and create an S3 bucket.
- Go to SQS and create a FIFO queue.
- Go to your queue settings and select the option 'Content-based deduplication'.
- Create an IAM user and attach the policy **s3_sqs_access.json** from this repository.
- Create access keys for the user.

### setup RunPod

- Go to [RunPod](https://runpod.io?ref=560tnscq).
- Go to **secure cloud** and launch an RTX A6000 pod.
- Select template **RunPod Stable Diffusion**. Unselect **Start Jupyter Notebook**.
- SSH into your pod.
- Execute these commands:

      git clone ...

- Download the files **execute_pipeline.py**, **credentials.py**, **variables.py** and **prompts.py** from this repository.
- Go to **credentials.py** and update it with the access keys credentials you created.
- Go to **variables.py** and update it with the name of your S3 bucket and the URL of your SQS queue.
- Execute the file

      python execute_pipeline.py

### python app

- Clone this repository.
- Install requirements.
- Go to **credentials.py** and update it with the access keys credentials you created.
- Go to **variables.py** and update it with the name of your S3 bucket and the URL of your SQS queue.
- Have fun !

## next steps

- Web app.
- Model training and inference in a serverless service.
- Explore other technologies for face / person generation.
