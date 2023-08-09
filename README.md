# dreambooth-stable-diffusion-python-tkinter

<p align="center">
<a href="https://www.youtube.com/watch?v=_yjNLzUwFhA">
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

- Go to [RunPod](https://bit.ly/451svCO).
- Go to **secure cloud** and launch an RTX A6000 pod.
- Select template **RunPod Stable Diffusion**. Unselect **Start Jupyter Notebook**.
- SSH into your pod.
- Execute these commands:

      git clone https://github.com/JoePenna/Dreambooth-Stable-Diffusion
      wget https://huggingface.co/panopstor/EveryDream/resolve/main/sd_v1-5_vae.ckpt
      apt install zip -y
      mkdir Dreambooth-Stable-Diffusion/training_images
      mv sd_v1-5_vae.ckpt Dreambooth-Stable-Diffusion/model.ckpt
      git clone https://github.com/djbielejeski/Stable-Diffusion-Regularization-Images-person_ddim.git
      mkdir -p Dreambooth-Stable-Diffusion/regularization_images/person_ddim
      mv -v Stable-Diffusion-Regularization-Images-person_ddim/person_ddim/*.* Dreambooth-Stable-Diffusion/regularization_images/person_ddim/
      cd Dreambooth-Stable-Diffusion
      pip install -e .
      pip install boto3
      pip install pytorch-lightning==1.7.6
      pip install torchmetrics==0.11.1
      pip install -e git+https://github.com/CompVis/taming-transformers.git@master#egg=taming-transformers
      pip install captionizer

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
- Execute **main.py**.
- Have fun !

## next steps

- Web app.
- Model training and inference in a serverless service.
- Explore other technologies for face / person generation.
