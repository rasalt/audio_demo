#Reference: https://cloud.google.com/speech-to-text/docs/async-recognize
#https://google-cloud-python.readthedocs.io/en/0.32.0/storage/blobs.html

from google.cloud import speech_v1p1beta1 as speech
from google.cloud.storage import Blob
from google.cloud import storage

client = speech.SpeechClient()

def diarize(data, context):

      
  speech_file = data['name']
  bucket = data['bucket']
  print('Bucket {}'.format(bucket))
  print('File {}'.format(speech_file))
  filename_uri = "gs://"+bucket+"/"+speech_file
  print('File name uri {}'.format(filename_uri))
  dest_file = speech_file+".txt"

  audio = speech.types.RecognitionAudio(uri=filename_uri)
  config = speech.types.RecognitionConfig(
      encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
      sample_rate_hertz=8000,
      language_code='en-US',
      enable_speaker_diarization=True,
      diarization_speaker_count=2)

  operation = client.long_running_recognize(config, audio)
  print('Waiting for operation to complete...')

# The transcript within each result is separate and sequential per result.
# However, the words list within an alternative includes all the words
# from all the results thus far. Thus, to get all the words with speaker
# tags, you only have to take the words list from the last result:
  #print(response.results)
  response = operation.result(timeout=300)
  result = response.results[-1]
  words_info = result.alternatives[0].words
  writestring = '' 
  for word_info in words_info:
     writestring += "Word: {} Speaker Tag: {}\n".format(word_info.word,word_info.speaker_tag)
  storage_client = storage.Client()
  bucket = storage_client.get_bucket(bucket)
  blob = Blob(dest_file, bucket)
  blob.upload_from_string(writestring)

def main():
  data = dict()  
  data['name'] = "commercial_mono.wav"
  data['bucket'] = "diarize_demo"
  diarize(data,0)


if __name__ == "__main__":
    main()
