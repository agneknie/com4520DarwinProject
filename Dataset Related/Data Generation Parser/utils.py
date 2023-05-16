import string

def find_idiom(needle, haystack):
  
  needle = needle.lower()
  haystack = haystack.lower()
  
  search_start = 0
  while (search_start < len(haystack)):
    index = haystack.find(needle, search_start)
    if index == -1:
      return False
    is_prefix_whitespace = (index == 0 or haystack[index-1] in string.whitespace)
    search_start = index + len(needle)
    is_suffix_whitespace = (search_start == len(haystack) or haystack[search_start] in string.whitespace)
    if (is_prefix_whitespace and is_suffix_whitespace):
      return True
  return False