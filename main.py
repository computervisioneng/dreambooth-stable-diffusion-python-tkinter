import os
import sys
import json
from pathlib import Path

import tkinter as tk
import tkinter.font as font
from tkinter.filedialog import asksaveasfile, askopenfilename
from PIL import ImageTk, Image
import boto3

import credentials
from variables import *
from prompts import DEFAULT_PROMPTS
from util import _from_rgb, generate_random_string, get_custom_prompts, write_custom_prompts


class App:
    def __init__(self):

        ###########################################################
        ### create main window ####################################
        ###########################################################

        self.main_window = tk.Tk()
        self.main_window.geometry("{}x{}".format(self.main_window.winfo_screenwidth(),
                                                 self.main_window.winfo_screenheight()))
        self.main_window.configure(bg="white")

        ###########################################################
        ### download models and images from previous executions ###
        ###########################################################

        self.sqs = boto3.client('sqs',
                           region_name='us-east-1',
                           aws_access_key_id=credentials.AWS_ACCESS_KEY,
                           aws_secret_access_key=credentials.AWS_SECRET_ACCESS_KEY)

        self.s3_client = boto3.client('s3',
                                      aws_access_key_id=credentials.AWS_ACCESS_KEY,
                                      aws_secret_access_key=credentials.AWS_SECRET_ACCESS_KEY)

        self.get_filenames(S3_BUCKET_MODELS_PREFIX)
        self.download(S3_BUCKET_IMGS_PREFIX)

        ###########################################################
        ### create side bar and main section ######################
        ###########################################################

        self.side_bar_label = tk.Label(self.main_window, width=50, height=50, bg=_from_rgb((100, 100, 100)))
        self.side_bar_label.place(x=150, y=90)
        self.create_side_bar_widgets()

        self.main_section_label = tk.Label(self.main_window, width=150, height=50, bg='white')
        self.main_section_label.place(x=600, y=90)

    def create_main_section_image_view(self):

        ###########################################################
        ### images ################################################
        ###########################################################

        self.main_img_label = tk.Label(self.main_section_label, bg='white')
        self.img_00_label = tk.Label(self.main_section_label, bg='white')
        self.img_01_label = tk.Label(self.main_section_label, bg='white')
        self.img_02_label = tk.Label(self.main_section_label, bg='white')
        self.img_03_label = tk.Label(self.main_section_label, bg='white')
        self.img_04_label = tk.Label(self.main_section_label, bg='white')
        self.img_05_label = tk.Label(self.main_section_label, bg='white')
        self.img_06_label = tk.Label(self.main_section_label, bg='white')
        self.img_07_label = tk.Label(self.main_section_label, bg='white')

        ###########################################################
        ### buttons ###############################################
        ###########################################################

        self.save_img_button = tk.Button(self.main_section_label, height=1, width=12, text="SAVE IMAGE", bg='white',
                                         font=font.Font(size=30), command=self.save_main_img)

        image_right_ = Image.open('./assets/right.png').resize((55, 55), Image.ANTIALIAS)
        image_right = ImageTk.PhotoImage(image_right_)

        self.move_right_button = tk.Button(self.main_section_label, height=1, width=1, bg='white',
                                           command=self.move_right)
        self.move_right_button.configure(image=image_right, width=55, height=55)
        self.move_right_button.image = image_right

        image_left_ = image_right_.rotate(180)
        image_left = ImageTk.PhotoImage(image_left_)

        self.move_left_button = tk.Button(self.main_section_label, height=1, width=1, bg='white',
                                          command=self.move_left)
        self.move_left_button.configure(image=image_left, width=55, height=55)
        self.move_left_button.image = image_left

    def create_side_bar_widgets(self):

        ###########################################################
        ### train new model #######################################
        ###########################################################

        self.train_new_model_button = tk.Button(self.side_bar_label, text='Train new model', height=1, width=15,
                                                bg='white',
                                                command=self.train_new_model)
        self.train_new_model_button.place(x=90, y=140)

        ###########################################################
        ### select model dropdown menu ############################
        ###########################################################

        self.select_model_label = tk.Label(self.side_bar_label, text='Select model:',
                                           font=("Arial", 25),
                                           bg=_from_rgb((100, 100, 100)), fg='white')
        self.select_model_label.place(x=30, y=50)

        if not os.path.exists(S3_BUCKET_MODELS_PREFIX):
            os.makedirs(S3_BUCKET_MODELS_PREFIX, exist_ok=True)
        models = [j for j in os.listdir(S3_BUCKET_MODELS_PREFIX)]
        models = ['                                         '] + models
        self.selected_model_ = tk.StringVar()
        self.selected_model_.set(models[0])
        self.select_model_dropdown = tk.OptionMenu(
            self.side_bar_label,
            self.selected_model_,
            *models,
            command=self.display_selected_model
        )
        self.select_model_dropdown.place(x=30, y=100)

        ###########################################################
        ### select style dropdown menu ############################
        ###########################################################

        self.select_style_label = tk.Label(self.side_bar_label, text='Select style:',
                                           font=("Arial", 25),
                                           bg=_from_rgb((100, 100, 100)), fg='white')
        self.select_style_label.place(x=30, y=200)

        custom_prompts_ = get_custom_prompts()
        styles = ['                                         '] + list(DEFAULT_PROMPTS.keys()) + \
                 list(custom_prompts_.keys()) + ['CUSTOM PROMPT']

        self.selected_style_ = tk.StringVar()
        self.selected_style_.set(styles[0])
        self.select_style_dropdown = tk.OptionMenu(
            self.side_bar_label,
            self.selected_style_,
            *styles,
            command=self.display_selected_style
        )
        self.select_style_dropdown.place(x=30, y=250)

        ###########################################################
        ### custom prompt text box ################################
        ###########################################################

        self.prompt_label = tk.Label(self.side_bar_label, text='Prompt:',
                                     font=("Arial", 25),
                                     bg=_from_rgb((100, 100, 100)),
                                     fg='white')
        self.prompt_label.place(x=30, y=350)

        self.custom_prompt_text_box = tk.Text(self.side_bar_label, height=6, width=25, font=font.Font(size=15))
        self.custom_prompt_text_box.config(state="disabled", bg=_from_rgb((220, 220, 220)))
        self.custom_prompt_text_box.place(x=30, y=400)

        ###########################################################
        ### 'GENERATE' button #####################################
        ###########################################################

        self.generate_button = tk.Button(self.side_bar_label, height=3, width=12, text="GENERATE", bg='white',
                                         font=font.Font(size=30), command=self.generate_images)
        self.generate_button.place(x=34, y=630)

        ###########################################################
        ### 'REFRESH' button ######################################
        ###########################################################

        image_refresh_ = Image.open('./assets/refresh.png').resize((55, 55), Image.ANTIALIAS)
        image_refresh = ImageTk.PhotoImage(image_refresh_)

        self.refresh_button = tk.Button(self.side_bar_label, height=1, width=1, bg=_from_rgb((100, 100, 100)),
                                        command=self.refresh)
        self.refresh_button.configure(image=image_refresh, width=55, height=55)
        self.refresh_button.image = image_refresh
        self.refresh_button.place(x=320, y=20)

    def open_file_dialog_box(self):
        self.file_to_upload = askopenfilename()

        self.display_filename = tk.Label(self.main_section_label, text=self.file_to_upload.split(os.sep)[-1],
                                         font=("Arial", 14), bg='white')
        self.display_filename.place(x=190, y=245)

    def train_new_model(self):

        for att in ['main_img_label', 'img_00_label', 'img_01_label', 'img_02_label', 'img_03_label', 'img_04_label',
                    'img_05_label', 'img_06_label', 'img_07_label', 'save_img_button', 'move_left_button',
                    'move_right_button']:
            if att in self.__dict__.keys():
                self.__getattribute__(att).place_forget()

        self.training_data_label = tk.Label(self.main_section_label, text='Training data', font=("Arial", 24), bg='white')
        self.training_data_label.place(x=20, y=20)

        self.training_data_instructions_label = tk.Label(self.main_section_label,
                                                         text='At least 20 images, like this:\n'
                                                              '     2–3 full body\n'
                                                              '     3–5 upper body\n'
                                                              '     5–12 close-up on face\n'
                                                              'Zip the images into a zip file.',
                                                         font=("Arial", 18),
                                                         justify='left',
                                                         bg='white')
        self.training_data_instructions_label.place(x=20, y=80)

        self.select_images = tk.Button(self.main_section_label, text='Select file...', height=1, width=15,
                                                bg='white',
                                                command=self.open_file_dialog_box)
        self.select_images.place(x=20, y=240)

        self.name_model_label = tk.Label(self.main_section_label, text='How do you want to name the model?',
                                         font=("Arial", 24), bg='white')
        self.name_model_label.place(x=20, y=480)

        self.name_model_text_box = tk.Text(self.main_section_label, height=2, width=25, font=font.Font(size=12))
        self.name_model_text_box.place(x=20, y=530)

        self.steps_per_image_label = tk.Label(self.main_section_label, text='Steps per image:',
                                              font=("Arial", 24), bg='white')
        self.steps_per_image_label.place(x=20, y=320)

        self.steps_per_image_text_box = tk.Text(self.main_section_label, height=2, width=25, font=font.Font(size=12))
        self.steps_per_image_text_box.place(x=20, y=370)

        self.upload_and_train_button = tk.Button(self.main_section_label, text='TRAIN!', height=3, width=15,
                                                 bg='white',
                                                 font=font.Font(size=30),
                                                 command=self.upload_file_to_s3_and_train)

        self.upload_and_train_button.place(x=20, y=630)

    def upload_file_to_s3_and_train(self):
        training_images_key = S3_BUCKET_TRAINING_DATA_PREFIX + '/' + self.file_to_upload.split(os.sep)[-1]
        self.s3_client.upload_file(self.file_to_upload, S3_BUCKET_NAME, training_images_key)

        response = self.train_dreambooth(self.name_model_text_box.get("1.0", 'end-1c'),
                                         self.steps_per_image_text_box.get("1.0", 'end-1c'),
                                         training_images_key)

        if True:  # TODO: change response status
            tk.messagebox.showinfo("Thank you!", "The training process has started!\nPlease come back later.")
        else:
            tk.messagebox.showinfo("ERROR", "Please try again.")

    def refresh(self):
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def get_filenames(self, prefix):

        response = self.s3_client.list_objects_v2(
            Bucket=S3_BUCKET_NAME,
            Prefix=prefix)

        for content in response.get('Contents', []):
            if not os.path.exists(content['Key']):
                filename = content['Key'].split('/')[-1]
                os.makedirs(os.path.join(content['Key'][:-len(filename)]), exist_ok=True)
                Path(content['Key']).touch()

    def download(self, prefix):

        response = self.s3_client.list_objects_v2(
            Bucket=S3_BUCKET_NAME,
            Prefix=prefix)

        for content in response.get('Contents', []):
            if content['Key'].endswith('.jpg') and not os.path.exists(content['Key']):
                filename = content['Key'].split('/')[-1]
                os.makedirs(os.path.join(content['Key'][:-len(filename)]), exist_ok=True)
                self.s3_client.download_file(S3_BUCKET_NAME, content['Key'], content['Key'])


    def train_dreambooth(self, name, steps_per_image, training_images_key):

        response = self.sqs.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=json.dumps({'mode': 'train',
                                    "model_url": "{}/{}.ckpt".format(S3_BUCKET_MODELS_PREFIX, name),
                                    "steps_per_image": steps_per_image,
                                    "training_images": training_images_key
                                    }
                                   ),
            MessageGroupId=generate_random_string(10))

        return response

    def generate_image_dreambooth(self, style, prompt):

        response = self.sqs.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=json.dumps({'mode': 'inference',
                                   'prompt': prompt,
                                    'out_img_dir': "{}/{}/{}".format(S3_BUCKET_IMGS_PREFIX,
                                                                     self.selected_model,
                                                                     style.lower().replace(' ', '')),
                                    'model_key': S3_BUCKET_MODELS_PREFIX + '/' + self.selected_model}
                                   ),
            MessageGroupId=generate_random_string(10))

        return response

    def move_right(self):

        self.current_main_image_index += 1
        self.current_main_image_index %= len(self.current_img_dir_list)

        self.set_main_image()

    def move_left(self):
        self.current_main_image_index -= 1
        self.current_main_image_index %= len(self.current_img_dir_list)

        self.set_main_image()

    def save_main_img(self):
        file = asksaveasfile()

        img_path_ = self.current_img_dir_list[self.current_main_image_index]

        img = Image.open(img_path_).resize((760, 760), Image.ANTIALIAS)

        img = img.convert('RGB')

        img.save(file.name)

    def set_main_image(self):

        img_path_ = self.current_img_dir_list[self.current_main_image_index]

        bg_ = Image.open(img_path_).resize((760, 760), Image.ANTIALIAS)
        bg = ImageTk.PhotoImage(bg_)
        self.main_img_label.configure(image=bg, width=760, height=760)
        self.main_img_label.image = bg

    def generate_images(self):

        self.create_main_section_image_view()

        self.current_main_image_index = 0

        imgs = [self.img_00_label, self.img_01_label, self.img_02_label, self.img_03_label,
                self.img_04_label, self.img_05_label, self.img_06_label, self.img_07_label]

        if self._selected_model_on_file() and self._selected_style_on_file() and self._selected_style_contains_imgs():
            for j, img_path in enumerate(sorted(
                    os.listdir(os.path.join(S3_BUCKET_IMGS_PREFIX, self.selected_model,
                                            self.selected_style.lower().replace(' ', ''))))):
                img_path_ = os.path.join(S3_BUCKET_IMGS_PREFIX,
                                         self.selected_model,
                                         self.selected_style.lower().replace(' ', ''),
                                         img_path)

                self.set_img_in_label(img_path_, imgs[j])

            self.current_main_image_index = 0
            self.current_img_dir_list = [os.path.join(S3_BUCKET_IMGS_PREFIX, self.selected_model,
                                                      self.selected_style.lower().replace(' ', ''), k)
                                         for k in sorted(os.listdir(os.path.join(S3_BUCKET_IMGS_PREFIX,
                                                                                 self.selected_model,
                                                                                 self.selected_style.lower().replace(' ', ''))))]
            self.set_main_image()

            self.main_img_label.place(x=0, y=0)
            self.img_00_label.place(x=780, y=0)
            self.img_01_label.place(x=1000, y=0)
            self.img_02_label.place(x=780, y=220)
            self.img_03_label.place(x=1000, y=220)
            self.img_04_label.place(x=780, y=440)
            self.img_05_label.place(x=1000, y=440)
            self.img_06_label.place(x=780, y=660)
            self.img_07_label.place(x=1000, y=660)
            self.save_img_button.place(x=210, y=780)
            self.move_left_button.place(x=0, y=780)
            self.move_right_button.place(x=700, y=780)

        elif self.selected_style not in ['CUSTOM PROMPT'] and self.selected_style not in get_custom_prompts():
            response = self.generate_image_dreambooth(self.selected_style, DEFAULT_PROMPTS[self.selected_style])
            print(response)

            if True:  # TODO: change response status
                tk.messagebox.showinfo("Thank you!", "Image generation has started!\nPlease come back later.")
            else:
                tk.messagebox.showinfo("ERROR", "Please try again.")

        elif self.selected_style in ['CUSTOM PROMPT']:
            name = 'custom-prompt-{}'.format(generate_random_string(5).lower())
            custom_prompts_ = get_custom_prompts()
            custom_prompts_[name] = self.custom_prompt_text_box.get("1.0", 'end-1c')
            write_custom_prompts(custom_prompts_)
            id = self.generate_image_dreambooth(name, self.custom_prompt_text_box.get("1.0", 'end-1c'))
            print(id)

            if True:  # TODO: change response status
                tk.messagebox.showinfo("Thank you!", "Image generation has started!\nPlease come back later.")
            else:
                tk.messagebox.showinfo("ERROR", "Please try again.")

        else:
            custom_prompts_ = get_custom_prompts()
            id = self.generate_image_dreambooth(self.selected_style, [custom_prompts_[self.selected_style]])
            print(id)

            if True:  # TODO: change response status
                tk.messagebox.showinfo("Thank you!", "Image generation has started!\nPlease come back later.")
            else:
                tk.messagebox.showinfo("ERROR", "Please try again.")

    def _selected_style_contains_imgs(self):
        return len(os.listdir(os.path.join(S3_BUCKET_IMGS_PREFIX, self.selected_model,
                                           self.selected_style.lower().replace(' ', '')))) > 0
    def _selected_style_on_file(self):
        return (self.selected_style.lower().replace(' ', '') in
                os.listdir(os.path.join(S3_BUCKET_IMGS_PREFIX, self.selected_model)))

    def _selected_model_on_file(self):
        return self.selected_model in os.listdir(S3_BUCKET_IMGS_PREFIX)

    def set_img_in_label(self, img_path_, img):
        bg_ = Image.open(img_path_).resize((200, 200), Image.ANTIALIAS)
        bg = ImageTk.PhotoImage(bg_)
        img.configure(image=bg, width=200, height=200)
        img.image = bg

    def display_selected_style(self, options):
        self.selected_style = self.selected_style_.get()
        if 'CUSTOM PROMPT' in options:
            self.custom_prompt_text_box.config(state="normal", bg='white')
        else:
            self.custom_prompt_text_box.delete('1.0', tk.END)
            self.custom_prompt_text_box.config(state="disabled", bg=_from_rgb((220, 220, 220)))

    def display_selected_model(self, options):
        self.selected_model = self.selected_model_.get()

    def start(self):
        self.main_window.mainloop()


if __name__ == "__main__":
    app = App()
    app.start()
