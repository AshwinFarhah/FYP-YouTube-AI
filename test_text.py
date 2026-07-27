from modules.text_features import extract_text_features


sample_text = """

Learn numbers with animals.

Count one two three.

Learn colours and shapes.

Let's learn again.

Subscribe and watch more fun videos.

"""


features = extract_text_features(
    sample_text
)


for key,value in features.items():

    print(
        key,
        ":",
        value
    )