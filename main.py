#Reference: https://cloud.google.com/speech-to-text/docs/async-recognize
from google.cloud import speech_v1p1beta1 as speech
import cloudstorage as gcs
#from google.cloud import storage as gcs

client = speech.SpeechClient()

def diarize(data, context):

      
  speech_file = data['name']
  bucket = data['bucket']
  
  print('Bucket {}'.format(bucket))
  print('File {}'.format(speech_file))
#  gcs_file = gcs.download_blob(bucket, speech_file)
#  with open(gcs_file, 'rb') as audio_file:
#     content = audio_file.read()
  filename = "gs://"+bucket+"/"+speech_file
  print("filename {}".format(filename))
  gcs_file = gcs.open(filename)
  content = gcs_file.read()
  audio = speech.types.RecognitionAudio(content=content)

  config = speech.types.RecognitionConfig(
      encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
      sample_rate_hertz=8000,
      language_code='en-US',
      enable_speaker_diarization=True,
      diarization_speaker_count=2)

  print('Waiting for operation to complete...')
  response = client.recognize(config, audio)

# The transcript within each result is separate and sequential per result.
# However, the words list within an alternative includes all the words
# from all the results thus far. Thus, to get all the words with speaker
# tags, you only have to take the words list from the last result:
  result = response.results[-1]

  words_info = result.alternatives[0].words

# Printing out the output:
  dest_file = gcs_file+".txt"
  file = open(dest_file,"w") 
  for word_info in words_info:
      file.write("word: '{}', speaker_tag: {} \n".format(word_info.word,
                                          word_info.speaker_tag))
  file.close()
  gcs.upload_blob('diarize_demo', dest_file)


def main():
  data = dict()  
  data['name'] = "commercial_mono.wav"
  data['bucket'] = "diarize_demo"
  diarize(data,0)
#        diarize('gs://diarize_demo/commercial_mono.wav')


if __name__ == "__main__":
    main()
