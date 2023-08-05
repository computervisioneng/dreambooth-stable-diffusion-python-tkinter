import shutil
import time
import ast
import random
import string
import os
import json

import boto3

import credentials
import variables
import prompts


def generate_random_string(N=20):
    return ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase) for i in range(N))


sqs = boto3.client('sqs',
                   region_name='us-east-1',
                   aws_access_key_id=credentials.AWS_ACCESS_KEY,
                   aws_secret_access_key=credentials.AWS_SECRET_ACCESS_KEY)

s3_client = boto3.client('s3',
                         aws_access_key_id=credentials.AWS_ACCESS_KEY,
                         aws_secret_access_key=credentials.AWS_SECRET_ACCESS_KEY)

queue_url = variables.SQS_QUEUE_URL

while True:

    # Receive message from SQS queue
    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=1
    )

    if 'Messages' not in response.keys():
        print('sleeping...')
        time.sleep(60)

    else:

        message = response['Messages'][0]
        receipt_handle = message['ReceiptHandle']

        message = ast.literal_eval(message['Body'])
        print(message)

        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )

        bucket_name = variables.S3_BUCKET_NAME

        mode = message['mode']

        if mode in ['inference']:

            model_path = message['model_key']
            out_imgs_s3_folder = message['out_img_dir']
            prompt = message['prompt']

            prompt = prompt.replace('@me', 'http person')

            model_path = './trained_models/' + model_path.split('/')[-1]

            output_dir = generate_random_string()

            os.system(
                'python scripts/stable_txt2img.py --ddim_eta 0.0 --n_samples 8 --n_iter 1 --scale 7.0 --ddim_steps 50 '
                '--ckpt ./{} --prompt "{}" --outdir {}'.format(
                    model_path, prompt, output_dir))

            for j in os.listdir('./{}/samples'.format(output_dir)):
                filename = './{}/samples/{}'.format(output_dir, j)

                if os.path.isfile(filename) and filename.endswith('.jpg'):

                    response = s3_client.upload_file(filename, bucket_name, os.path.join(out_imgs_s3_folder, j))

            shutil.rmtree(output_dir)

        elif mode in ['train']:

            # This isn't used for training, just to help you remember what your trained into the model.
            project_name = generate_random_string(N=20)

            training_images_key = message['training_images']
            out_model_key = message['model_url']
            number_steps_per_image = int(message['steps_per_image'])

            training_images_zip_filename = './{}.zip'.format(project_name)

            s3_client.download_file(bucket_name, training_images_key, training_images_zip_filename)

            os.makedirs('training_images/{}'.format(project_name))

            os.system('unzip {} -d training_images/{}/'.format(training_images_zip_filename, project_name))

            nmr_images = len(os.listdir('training_images/{}/'.format(project_name)))

            # MAX STEPS
            # How many steps do you want to train for?
            max_training_steps = int(nmr_images * number_steps_per_image)
            # max_training_steps = 10

            # Match class_word to the category of the regularization images you chose above.
            class_word = "person"  # typical uses are "man", "person", "woman"

            # If you are training a person's face, set this to True
            i_am_training_a_persons_face = True

            flip_p_arg = 0.0 if i_am_training_a_persons_face else 0.5

            # This is the unique token you are incorporating into the stable diffusion model.
            token = "http"

            # 0 Saves the checkpoint when max_training_steps is reached.
            # 250 saves the checkpoint every 250 steps as well as when max_training_steps is reached.
            save_every_x_steps = 0

            reg_data_root = "regularization_images/person_ddim"

            os.system(
                'python main.py --debug False --training_model model.ckpt --regularization_images {} --project_name {} '
                '--training_images training_images/{}/ --max_training_steps {} '
                '--class_word {} --token {} --flip_p {} --save_every_x_steps {}'.format(
                    reg_data_root, project_name, project_name, max_training_steps, class_word, token, flip_p_arg,
                    save_every_x_steps))

            out_model_path = [j for j in os.listdir('./trained_models') if project_name in j and j.endswith('.ckpt')][0]
            shutil.move(os.path.join('./trained_models', out_model_path), os.path.join('./trained_models',
                                                                                       out_model_key.split('/')[-1]))

            response = s3_client.upload_file(os.path.join('./trained_models', out_model_key.split('/')[-1]),
                                             bucket_name,
                                             out_model_key)

            for prompt_name in prompts.DEFAULT_PROMPTS.keys():
                prompt = prompts.DEFAULT_PROMPTS[prompt_name]
                response = sqs.send_message(
                                    QueueUrl=variables.SQS_QUEUE_URL,
                                    MessageBody=json.dumps({'mode': 'inference',
                                                           'prompt': prompt,
                                                           'out_img_dir': "{}/{}/{}".format(variables.S3_BUCKET_IMGS_PREFIX,
                                                                                             out_model_key.split('/')[-1],
                                                                                             prompt_name.lower().replace(' ', '')),
                                                           'model_key': variables.S3_BUCKET_MODELS_PREFIX + '/' + out_model_key}
                                                           ),
                                    MessageGroupId=generate_random_string(10))
