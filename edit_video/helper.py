import os
import random
import string
import ffmpeg
import requests
import pandas as pd
from moviepy.editor import *
from azure.storage.blob import BlockBlobService, PublicAccess
from aws_transcript.models import Word, Transcript
from edit_video.serializers import WordEditSerializer
from pathlib import Path


def get_edit_video(net_score):
    clip_append = []
    word_data = Word.objects.all()
    serializer = WordEditSerializer(word_data, many=True)
    df_word = serializer.data
    concat_final_list = get_threshold_value(df_word, net_score)
    print("++++++++++concat_final_list+++++++++++++", concat_final_list)
    for val in concat_final_list:
        obj = Transcript.objects.get(pk=val["transcript_id"])
        video_full_url = obj.video_name
        if video_full_url:
            video_url = convert_file(video_full_url)
            print("++++++++++video_url+++++++++++++", video_url)
            clip_append.append(VideoFileClip(video_url).subclip(val["to_start"], val["to_end"]))
        else:
            status = False
            return status, "Given file not exist:-  " + val["transcript_id"]
    print("++++++++++clip_append+++++++++++++", clip_append)
    final_clip = concatenate_videoclips(clip_append, method='compose')
    output_video = get_random_text() + ".mp4"
    output_video_url = "media/" + output_video
    final_clip.write_videofile(output_video_url)
    blob_url = insert_file_in_azure(output_video)
    # blob_url = concat_final_list
    status = True
    remove_file()
    return status, blob_url


def get_random_text():
    char_set = string.ascii_uppercase + string.digits
    random_text = ''.join(random.sample(char_set * 6, 6))
    return random_text


def convert_file(input_url):
    try:
        file_path = "converted/" + get_random_text() + ".mp4"
        stream = ffmpeg.input(input_url)
        stream = ffmpeg.output(stream, file_path)
        ffmpeg.run(stream)
        return file_path
    except Exception as e:
        return False


def convert_webm_to_mp4(input_url):
    try:
        filename = Path(input_url).stem + ".mp4"
        file_path = "media/" + filename
        stream = ffmpeg.input(input_url)
        stream = ffmpeg.output(stream, file_path)
        ffmpeg.run(stream)
        blob_url = insert_file_in_azure(filename)
        return blob_url
    except Exception as e:
        return False


def insert_file_in_azure(blob_name):
    account_name = 'sausprodwt01'
    account_key = 'ZwSETE0Dy/LdskhguZi6td8fZZaKLnr4y54Xmd4MvWpXH2GJhVhWmQZcEvRsbOWwjMY9466nmUH9AJCSPhSDmw=='
    project_root = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
    # Create the BlockBlockService that the system uses to call the Blob service for the storage account.
    block_blob_service = BlockBlobService(account_name=account_name, account_key=account_key)
    # Create a container called 'video'.
    container_name = 'video'
    block_blob_service.create_container(container_name)
    # Set the permission so the blobs are public.
    block_blob_service.set_container_acl(container_name, public_access=PublicAccess.Container)
    file_path = os.path.join(os.path.join(project_root, 'media'), blob_name)
    print(file_path)
    block_blob_service.create_blob_from_path(container_name, blob_name, file_path)
    os.remove(file_path)
    blob_url = f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}"
    return blob_url


def check_file(file_name):
    try:
        req = requests.head(file_name)
        if req.status_code == requests.codes.ok:
            print("url")
            return file_name
    except Exception as e:
        return False


def remove_file():
    project_root = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
    for f in os.listdir(os.path.join(project_root, 'converted')):
        try:
            os.remove(os.path.join(os.path.join(project_root, 'converted'), f))
        except Exception as e:
            pass


def get_threshold_value(df_word, net_score):
    df_word = pd.json_normalize(df_word)
    df_word['net_score'] = df_word['net_score'].astype(float)
    print(df_word['net_score'])
    # unique_vid = df_word.transcript_id.unique()
    df_word = df_word.dropna(subset=['start_time'])
    df_word.reset_index(inplace=True)

    # vidname = ()
    new_list = []
    # new_dict = {}
    # df_word['start_time'] = df_word['start_time'].astype(float)
    word_id_list = []
    start_time_list = []
    transcript_id_list = []
    end_time_list = []
    print("++++++++net_score+++++++++++", net_score)
    for k in range(0, len(df_word)):
        if net_score < 0:
            print("++++++++nig+++++++++++", net_score)
            net_score_k = df_word['net_score'][k] <= net_score
        else:
            print("++++++++posi+++++++++++", net_score)
            print("++++++++Ranger+++++++++++", k)
            net_score_k = df_word['net_score'][k] >= net_score

        # print("++++++++net_score+++++++++++", net_score)

        if net_score_k:
            if ((k - 3) >= 0) and ((k + 3) < (len(df_word) - 1)):
                word_id_list = df_word['id'][k]
                transcript_id_list = df_word['transcript_id'][k]
                # if df_word[(df_word['transcript_id'][k] == df_word['transcript_id'][k-3]) and (df_word['pron']  == 'pronunciation')]:
                if (df_word['transcript_id'][k] == df_word['transcript_id'][k - 3]):
                    start_time_list = df_word['start_time'][k - 3]
                elif (df_word['transcript_id'][k] == df_word['transcript_id'][k - 2]):
                    start_time_list = df_word['start_time'][k - 2]
                elif (df_word['transcript_id'][k] == df_word['transcript_id'][k - 1]):
                    start_time_list = df_word['start_time'][k - 1]
                else:
                    start_time_list = df_word['start_time'][k]

                if (df_word['transcript_id'][k] == df_word['transcript_id'][k + 3]):
                    end_time_list = df_word['end_time'][k + 3]
                elif (df_word['transcript_id'][k] == df_word['transcript_id'][k + 2]):
                    end_time_list = df_word['end_time'][k + 2]
                elif (df_word['transcript_id'][k] == df_word['transcript_id'][k + 1]):
                    end_time_list = df_word['end_time'][k + 1]
                else:
                    end_time_list = df_word['end_time'][k]

                # print(word_id_list)
                # print(start_time_list)
                # print(end_time_list)
                # new_list = [word_id_list , start_time_list , end_time_list]
                new_list.append({"word_id": word_id_list, "to_start": start_time_list, "to_end": end_time_list,
                                 "transcript_id": transcript_id_list})
                # new_list1.append(new_list)
                # new_dict =
            elif ((k - 2) >= 0) and ((k + 2) < (len(df_word) - 1)):
                word_id_list = df_word['transcript_id'][k]
                if (df_word['transcript_id'][k] == df_word['transcript_id'][k - 2]):
                    start_time_list = df_word['start_time'][k - 2]
                elif (df_word['transcript_id'][k] == df_word['transcript_id'][k - 1]):
                    start_time_list = df_word['start_time'][k - 1]
                else:
                    start_time_list = df_word['start_time'][k]

                if (df_word['transcript_id'][k] == df_word['transcript_id'][k + 2]):
                    end_time_list = df_word['end_time'][k + 2]
                elif (df_word['transcript_id'][k] == df_word['transcript_id'][k + 1]):
                    end_time_list = df_word['end_time'][k + 1]
                else:
                    end_time_list = df_word['end_time'][k]
                # print(word_id_list)
                # print(start_time_list)
                # print(end_time_list)
                # new_list = [word_id_list , start_time_list , end_time_list]
                new_list.append({"word_id": word_id_list, "to_start": start_time_list, "to_end": end_time_list,
                                 "transcript_id": transcript_id_list})
                # new_list1.append(new_list)
            elif ((k - 1) >= 0) and ((k + 1) < (len(df_word) - 1)):
                word_id_list = df_word['transcript_id'][k]
                if (df_word['transcript_id'][k] == df_word['transcript_id'][k - 1]):
                    start_time_list = df_word['start_time'][k - 1]
                else:
                    start_time_list = df_word['start_time'][k]

                if (df_word['transcript_id'][k] == df_word['transcript_id'][k + 1]):
                    end_time_list = df_word['end_time'][k + 1]
                else:
                    end_time_list = df_word['end_time'][k]
                # print(word_id_list)
                # print(start_time_list)
                # print(end_time_list)
                # new_list = [word_id_list , start_time_list , end_time_list]
                new_list.append({"word_id": word_id_list, "to_start": start_time_list, "to_end": end_time_list,
                                 "transcript_id": transcript_id_list})

                # new_list1.append(new_list)
            elif ((k) >= 0) and ((k) < (len(df_word) - 1)):
                word_id_list = df_word['transcript_id'][k]
                start_time_list = df_word['start_time'][k]
                end_time_list = df_word['end_time'][k]
                print(word_id_list)
                print(start_time_list)
                print(end_time_list)
                # new_list = [word_id_list , start_time_list , end_time_list]
                new_list.append({"word_id": word_id_list, "to_start": start_time_list, "to_end": end_time_list,
                                 "transcript_id": transcript_id_list})
    random.shuffle(new_list)
    return new_list


def aggregate_data_word(df_word):
    df_word['net_score'] = df_word['net_score'].astype(float)

    Aggregate_data_word = pd.DataFrame(columns=['Question', 'Positive_count', 'Negative_count', 'Neutral_count',
                                                'Total_words', 'Positive_percent', 'Negative_percent',
                                                'Neutral_percent'])

    Aggregate_data_word['Question'] = Aggregate_data_word['Question'].astype(object)

    postive_Q1 = df_word.loc[(df_word['sentiment'] == 'POS') & (df_word['question'] == 1)]  # .sum()
    postive_Q1 = len(postive_Q1)

    negative_Q1 = df_word.loc[(df_word['sentiment'] == 'NEG') & (df_word['question'] == 1)]
    negative_Q1 = len(negative_Q1)

    neutral_Q1 = df_word.loc[(df_word['sentiment'] == 'NEU') & (df_word['question'] == 1)]
    neutral_Q1 = len(neutral_Q1)

    Total_Q1 = postive_Q1 + negative_Q1 + neutral_Q1

    Positive_percent1 = (postive_Q1 / Total_Q1) * 100

    Negative_percent1 = (negative_Q1 / Total_Q1) * 100

    Neutral_percent1 = (neutral_Q1 / Total_Q1) * 100

    List_question1 = '1', postive_Q1, negative_Q1, neutral_Q1, Total_Q1, Positive_percent1, Negative_percent1, Neutral_percent1

    List_question1_series = pd.Series(List_question1, index=Aggregate_data_word.columns)

    Aggregate_data_word = Aggregate_data_word.append(List_question1_series, ignore_index=True)

    postive_Q2 = df_word.loc[(df_word['sentiment'] == 'POS') & (df_word['question'] == 2)]
    postive_Q2 = len(postive_Q2)

    negative_Q2 = df_word.loc[(df_word['sentiment'] == 'NEG') & (df_word['question'] == 2)]
    negative_Q2 = len(negative_Q2)

    neutral_Q2 = df_word.loc[(df_word['sentiment'] == 'NEU') & (df_word['question'] == 2)]
    neutral_Q2 = len(neutral_Q2)

    Total_Q2 = postive_Q2 + negative_Q2 + neutral_Q2

    Positive_percent2 = (postive_Q2 / Total_Q2) * 100

    Negative_percent2 = (negative_Q2 / Total_Q2) * 100

    Neutral_percent2 = (neutral_Q2 / Total_Q2) * 100

    List_question2 = '2', postive_Q2, negative_Q2, neutral_Q2, Total_Q2, Positive_percent2, Negative_percent2, Neutral_percent2

    List_question2_series = pd.Series(List_question2, index=Aggregate_data_word.columns)

    Aggregate_data_word = Aggregate_data_word.append(List_question2_series, ignore_index=True)

    postive_Q3 = df_word.loc[(df_word['sentiment'] == 'POS') & (df_word['question'] == 3)]
    postive_Q3 = len(postive_Q3)

    negative_Q3 = df_word.loc[(df_word['sentiment'] == 'NEG') & (df_word['question'] == 3)]
    negative_Q3 = len(negative_Q3)

    neutral_Q3 = df_word.loc[(df_word['sentiment'] == 'NEU') & (df_word['question'] == 3)]
    neutral_Q3 = len(neutral_Q3)

    Total_Q3 = postive_Q3 + negative_Q3 + neutral_Q3

    Positive_percent3 = (postive_Q3 / Total_Q3) * 100

    Negative_percent3 = (negative_Q3 / Total_Q3) * 100

    Neutral_percent3 = (neutral_Q3 / Total_Q3) * 100

    List_question3 = '3', postive_Q3, negative_Q3, neutral_Q3, Total_Q3, Positive_percent3, Negative_percent3, Neutral_percent3

    List_question3_series = pd.Series(List_question3, index=Aggregate_data_word.columns)

    Aggregate_data_word = Aggregate_data_word.append(List_question3_series, ignore_index=True)

    Positive_total = postive_Q1 + postive_Q2 + postive_Q3

    Negative_total = negative_Q1 + negative_Q2 + negative_Q2

    Neutral_total = neutral_Q1 + neutral_Q2 + neutral_Q3

    Total_words = Total_Q1 + Total_Q2 + Total_Q3

    Positive_percent_total = (Positive_total / Total_words) * 100

    Negative_percent_total = (Negative_total / Total_words) * 100

    Neutral_percent_total = (Neutral_total / Total_words) * 100

    List_total = 'All', Positive_total, Negative_total, Neutral_total, Total_words, Positive_percent_total, Negative_percent_total, Neutral_percent_total

    List_total_series = pd.Series(List_total, index=Aggregate_data_word.columns)

    Aggregate_data_word = Aggregate_data_word.append(List_total_series, ignore_index=True)

    js = Aggregate_data_word.to_json(orient='records')
    return js


def aggregate_data_transcript(df_tran):
    Aggregate_data_tran = pd.DataFrame(columns=['Question', 'Positive_count', 'Negative_count', 'Neutral_count'])

    Aggregate_data_tran['Question'] = Aggregate_data_tran['Question'].astype(object)
    df_tran['score_per_statement'] = df_tran['score_per_statement'].astype(float)

    postive_Q1 = df_tran.loc[(df_tran['score_per_statement'] >= 15) & (df_tran['question'] == 1)]
    postive_Q1 = len(postive_Q1)

    negative_Q1 = df_tran.loc[(df_tran['score_per_statement'] < 0) & (df_tran['question'] == 1)]
    negative_Q1 = len(negative_Q1)

    neutral_Q1 = df_tran.loc[
        (df_tran['score_per_statement'] < 15) & (df_tran['score_per_statement'] >= 0) & (df_tran['question'] == 1)]
    neutral_Q1 = len(neutral_Q1)

    List_question1 = '1', postive_Q1, negative_Q1, neutral_Q1
    List_question1_series = pd.Series(List_question1, index=Aggregate_data_tran.columns)

    Aggregate_data_tran = Aggregate_data_tran.append(List_question1_series, ignore_index=True)

    postive_Q2 = df_tran.loc[(df_tran['score_per_statement'] >= 15) & (df_tran['question'] == 2)]
    postive_Q2 = len(postive_Q2)

    negative_Q2 = df_tran.loc[(df_tran['score_per_statement'] < 0) & (df_tran['question'] == 2)]
    negative_Q2 = len(negative_Q2)

    neutral_Q2 = df_tran.loc[
        (df_tran['score_per_statement'] < 15) & (df_tran['score_per_statement'] >= 0) & (df_tran['question'] == 2)]
    neutral_Q2 = len(neutral_Q2)

    List_question2 = '2', postive_Q2, negative_Q2, neutral_Q2
    List_question2_series = pd.Series(List_question2, index=Aggregate_data_tran.columns)

    Aggregate_data_tran = Aggregate_data_tran.append(List_question2_series, ignore_index=True)

    postive_Q3 = df_tran.loc[(df_tran['score_per_statement'] > 15) & (df_tran['question'] == 3)]
    postive_Q3 = len(postive_Q3)

    negative_Q3 = df_tran.loc[(df_tran['score_per_statement'] < 0) & (df_tran['question'] == 3)]
    negative_Q3 = len(negative_Q3)

    neutral_Q3 = df_tran.loc[
        (df_tran['score_per_statement'] < 15) & (df_tran['score_per_statement'] >= 0) & (df_tran['question'] == 3)]
    neutral_Q3 = len(neutral_Q3)

    List_question3 = '3', postive_Q3, negative_Q3, neutral_Q3
    List_question3_series = pd.Series(List_question3, index=Aggregate_data_tran.columns)

    Aggregate_data_tran = Aggregate_data_tran.append(List_question3_series, ignore_index=True)

    Total_positive = postive_Q1 + postive_Q2 + postive_Q3

    Total_negative = negative_Q1 + negative_Q2 + negative_Q3

    Total_neutral = neutral_Q1 + neutral_Q2 + neutral_Q3

    List_total = 'All', Total_positive, Total_negative, Total_neutral

    List_total_series = pd.Series(List_total, index=Aggregate_data_tran.columns)

    Aggregate_data_tran = Aggregate_data_tran.append(List_total_series, ignore_index=True)

    js = Aggregate_data_tran.to_json(orient='records')
    return js
