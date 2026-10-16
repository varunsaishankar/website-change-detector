import cleaner

a = "Noisy page\nCurrent time: 12:08:58 PM\nVisitors: 48213 views\nReal content: version 1"
b = "Noisy page\nCurrent time: 12:09:02 PM\nVisitors: 977 views\nReal content: version 1"

print("Medium same?", cleaner.clean_text(a, "medium") == cleaner.clean_text(b, "medium"))
print("High same?  ", cleaner.clean_text(a, "high") == cleaner.clean_text(b, "high"))
print(repr(cleaner.clean_text(a, "medium")))