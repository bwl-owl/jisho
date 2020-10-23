import json, requests, argparse, os.path, csv, sys

parser = argparse.ArgumentParser(epilog='Note: because there are Japanese characters, you must use utf8 encoding when opening files (including this script)',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--outfile', help='output results CSV file name', default='jisho_results.csv')
parser.add_argument('--max_results', help='maximum results you want returned for a query', default=3)
args = parser.parse_args()

def concat_japanese_definitions(definition_info):
  concatenated = ''
  for info in definition_info:
    to_add = ''
    if 'word' in info:
      to_add = info['word']
      if 'reading' in info:
        to_add += " (% s)"% info['reading']
    elif 'reading' in info:
      to_add = info['reading']

    if to_add:
      concatenated += to_add + "\n"
  return concatenated

def concat_english_definitions(definition_info):
  concatenated = ''
  for info in definition_info:
    if 'english_definitions' in info:
      concatenated += ', '.join(info['english_definitions'])
      concatenated += '\n'
  return concatenated

jisho_api_endpoint = 'https://jisho.org/api/v1/search/words?keyword='

#continuously accept input until user quits
while True:
  print('Enter your query (as you would on jisho.org), or enter \'\q\' to quit: ', end='')
  query = input()

  if query == '\q':
    print("またね！")
    sys.exit(0)
  else:
    response = requests.get(jisho_api_endpoint + query)
    data = response.json()['data']

    if not data:
      print('No results found\n')
      continue;

    if not os.path.isfile(args.outfile):
      results_csv = open(args.outfile, 'x', newline='', encoding='utf-8')
      writer = csv.writer(results_csv, delimiter=',')
      header = ['Japanese', 'English', 'JLPT level']
      writer.writerow(header)
    else:
      results_csv = open(args.outfile, 'a', newline='', encoding='utf-8')
      writer = csv.writer(results_csv, delimiter=',')

    jisho_search_url = 'https://jisho.org/search/'
    for i in range(0, min(args.max_results, len(data))):
      entry = data[i]
      japanese = concat_japanese_definitions(entry['japanese'])
      english = concat_english_definitions(entry['senses'])
      jlpt_level = entry['jlpt'][0][-1:] if entry['jlpt'] else '-'
      jisho_link = jisho_search_url + entry['slug'] if entry['slug'] else ''

      print('Japanese:\n' + japanese)
      print('English:\n' + english)
      print('JLPT level: ' + jlpt_level)
      print('Jisho link for more info: ' + jisho_link)
      print('\n**********\n')

      writer.writerow([japanese, english, jlpt_level, jisho_link])

    results_csv.close()
