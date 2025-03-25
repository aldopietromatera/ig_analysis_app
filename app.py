import os
import streamlit as st
import pandas as pd
import shutil

st.set_page_config(page_title="Instagram Analysis", page_icon="📊")
st.title("Instagram Followers Analysis")

# For adding date and time to the file names when downloading
timestamp = pd.Timestamp("now")
timestamp = timestamp.strftime("%Y%m%d_%H%M%S")

# give me the important emojis


# Import the whole connections folder
connections = st.file_uploader(
    "Upload connections folder", type=["zip"], key="connections"
)
if not connections:
    st.info(
        """Please, download your data from the Instagram app and upload the connections ZIP here.

        How to download your data 🤔

            1. Open the Instagram app
            2. Go to your profile
            3. Click on the three lines in the top right corner
            4. Click on "Your Activity"
            5. Click on "Download you information" at the very bottom
            6. Click on "Download or transfer information"
            7. Select "Some of your information"
            8. Scroll down until the Contacts section and select
                "Follower and people/pages you follow"
            9. Click on "Next"
            10. Select "Download on your phone"
            11. Select the date range you want
            12. ⚠️ Select the JSON format (Important!)
            13. Click on "Create File"
            14. Wait for the email and download the ZIP file from it ⏳
            15. Upload the ZIP file here and Voilà! 🎉

            Note that the email may take some time to arrive...

        """
    )
if connections:
    import zipfile

    with zipfile.ZipFile(connections, "r") as zip_ref:
        zip_ref.extractall(
            "connections"
        )  # Extract all the contents into the 'connections' folder

    # Check if the 'followers.json' and 'following.json' files exist
    followers_path = "connections/connections/followers_and_following/followers_1.json"
    following_path = "connections/connections/followers_and_following/following.json"
    if not os.path.exists(followers_path) or not os.path.exists(following_path):
        st.error(
            "Please, be sure that the followers and following files are in the connections folder you just uploaded."
        )
        st.stop()
    else:
        st.success("Connections folder uploaded successfully.")

    # Read followers file
    df_followers = pd.read_json(followers_path)
    df_followers["username"] = df_followers["string_list_data"].apply(
        lambda x: x[0]["value"] if isinstance(x, list) and len(x) > 0 else None
    )

    # Read following file
    df_following = pd.read_json(following_path)
    df_following["username"] = df_following["relationships_following"].apply(
        lambda x: (
            x["string_list_data"][0]["value"].strip("")
            if isinstance(x, dict) and "string_list_data" in x
            else None
        )
    )

    # Get sets of followers and following
    following_set = set(df_following["username"].dropna())
    followers_set = set(df_followers["username"].dropna())

    # Users who don't follow back
    do_not_follow_back = following_set - followers_set
    df_not_following_back = pd.DataFrame(list(do_not_follow_back), columns=["username"])

    st.subheader("Users who don't follow you back")
    st.dataframe(df_not_following_back, height=200)

    # Download CSV file
    # df_not_following_back.to_csv("not_following_back.csv", index=False)
    st.download_button(
        "Download Not Following Back List in csv format",
        df_not_following_back.to_csv(index=False).encode("utf-8"),
        timestamp + "_not_following_back.csv",
        "text/csv",
    )

    # # Compare with previous data
    # previous_data = st.checkbox("Do you have the previous data to compare with?")
    # if previous_data:
    #     previous_data = st.file_uploader(
    #         "Upload previous not following back data", type=["csv"], key="previous_data"
    #     )
    #     if previous_data:
    #         df_not_following_back_previous = pd.read_csv(previous_data)
    #         df_not_following_back_diff = df_not_following_back[
    #             ~df_not_following_back["username"].isin(
    #                 df_not_following_back_previous["username"]
    #             )
    #         ]
    #         # df_not_following_back_diff.to_csv(
    #         #     "not_following_back_diff.csv", index=False
    #         # )

    #         st.subheader("Newly Detected Not Following Back")
    #         st.dataframe(df_not_following_back_diff)

    #         st.download_button(
    #             "Download Difference List in csv format",
    #             df_not_following_back_diff.to_csv(index=False).encode("utf-8"),
    #             timestamp + "_not_following_back_diff.csv",
    #             "text/csv",
    #         )

    # delete the connections folder
    shutil.rmtree("connections")
