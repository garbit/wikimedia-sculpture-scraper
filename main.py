import requests
import json
import time

# https://commons.wikimedia.org/w/api.php?action=query&format=json&list=categorymembers&cmtitle=Category:Sculptures_by_artist&cmlimit=max

SLEEP_DURATION = 0.25
SESSION = requests.Session()

def query_category_by_category_title(category, page = 0, cmcontinue = None):
  url = f"https://commons.wikimedia.org/w/api.php"

  params = {
    "action": "query",
    "format": "json",
    "list": "categorymembers",
    "cmtitle": category,
    "cmlimit": "max"
  }

  if cmcontinue:
    params["cmcontinue"] = cmcontinue

  response = SESSION.get(url, params=params)
  # print(response.url)

  json_response = response.json()

  time.sleep(SLEEP_DURATION)

  return json_response

def write_to_json(filename, data):
  with open(f'{filename}', 'w') as output_file:
    output_file.write(json.dumps(data, indent=4))


def query_category_by_pageid(pageid, parent_id = None):
  url = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&list=categorymembers&cmpageid={pageid}&cmlimit=max"

  params = {
    "action": "query",
    "format": "json",
    "list": "categorymembers",
    "cmpageid": pageid,
    "cmlimit": "max"
  }

  response = SESSION.get(url, params=params)
  print(response.url)

  json_response = response.json()

  save_path = ""
  if parent_id:
    save_path = f"{parent_id}/{pageid}"
  else:
    save_path = pageid

  write_to_json(f'{save_path}.json', json_response)

  time.sleep(SLEEP_DURATION)

  return json_response

def query_sub_categories(category):
  top_level_categories = []
  
  response = query_category_by_category_title(category, page=0, cmcontinue=None)
  
  category_members = response["query"]["categorymembers"]
  continue_param = response.get("continue", None)
  
  top_level_categories.extend(category_members)

  if continue_param != None:
    completed = False

    page = 1
    while not completed:
      result = query_category_by_category_title(category, page, continue_param.get("cmcontinue", None))

      page_n_category_members = result["query"]["categorymembers"]
      cm_continue = result.get('continue', None)

      top_level_categories.extend(page_n_category_members)

      if cm_continue == None:
        completed = True
      else:
        continue_param = cm_continue
      
      page = page + 1
  
  # print(f'found: {len(top_level_categories)} categories')
  # write_to_json(f'data/{category}_{parent_page_id}_results.json', sorted(top_level_categories, key=lambda x: x.get('title')))
  return top_level_categories

def load_json(filename):
  with open(filename) as fd:
     json_data = json.load(fd)
  return json_data

def crawl_category(category, parent_page_id=""):
  response = query_sub_categories(category)

  category_list = []

  print(f'crawling {category}')
  files = list(filter(lambda c: c["title"].startswith("File:"), response))
  sub_categories = list(filter(lambda c: not c["title"].startswith("File:"), response))

  if len(files) > 0:
    write_to_json(f'data/{category}_{parent_page_id}.json', files)

  category_list.extend(sub_categories)

  for index, c in enumerate(sub_categories):
    parent_page_id = f'{parent_page_id}_{index}'
    category_list.extend(crawl_category(c["title"], parent_page_id=parent_page_id))
  
  return category_list

# category = 'Category:Sculptures_by_artist'
category = "Category:Reliefs_by_artist"
category_pages = query_sub_categories(category)

write_to_json(f"{category}.json", crawl_category(category, 0))


# for c in category_pages:
#   print('---')
#   print(c["title"])
#   if not c["title"].startswith('File:'):
#     c_pages = c
#     parent_id = c["pageid"]
#     debug_output = c["title"]
#     while len(c_pages) > 0:
#       if not c["title"].startswith('File:'):
#         c_pages = crawl_all_category_pages(c["title"], parent_id)
#         if len(c_pages) > 0:
#           parent_id = f'{parent_id}_{c["pageid"]}'
#           debug_output = f'{debug_output} > {c["title"]}'
#           print(debug_output)
#           c["title"] = c_pages[0]["title"]
#         else:
#           c_pages = []
#       else:
#         c_pages = []

# load_json("Category:Sculptures_by_artist_results.json")
# crawl_categories(categories)
# print(load_json("Category:Sculptures_by_artist_results.json"))

      






