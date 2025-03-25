import os
import streamlit as st
import pandas as pd
import shutil
import zipfile

st.set_page_config(page_title="Instagram Analysis", page_icon="📊")
st.title("Who’s Not Following You Back on Instagram? 😎")
st.header(
    "Time to clean up your following list! Find out who isn’t following you back. 🔍"
)

# Privacy policy and terms of use
agree = st.checkbox(
    "I agree to use this app and to the [Streamlit's privacy policy](https://streamlit.io/privacy-policy)."
)

if not agree:
    st.warning("You must agree to the terms before using the app.")
    st.warning(
        """⚠️Your data remains private and is automatically deleted after the analysis."""
    )
    st.stop()

# For adding date and time to the file names when downloading
timestamp = pd.Timestamp("now")
timestamp = timestamp.strftime("%Y%m%d_%H%M%S")

# Import the whole connections folder
connections = st.file_uploader("Upload ZIP file here", type=["zip"], key="connections")
if not connections:
    st.info(
        """Please, download your data from the Instagram app and upload the ZIP here.

        How to Download Your Instagram Data 🤔

        1. Open the Instagram app.
        2. Go to your profile.
        3. Tap the three lines in the top right corner.
        4. Tap "Your Activity".
        5. Tap "Download Your Information" at the very bottom.
        6. Tap "Download or Transfer Your Information."
        7. ⚠️ Select "Some of Your Information" (not all your data...).
        8. Scroll down to the "Contacts" section and select "Followers and People/Pages You Follow".
        9. Tap "Next".
        10. Select "Download on Your Phone".
        11. Choose the desired date range.
        12. ⚠️ Select the JSON format (important!).
        13. Tap "Create File".
        14. Wait for the email and download the ZIP file from it ⏳.
        15. Upload the ZIP file here, and Voilà! 🎉

        Note: The email may take some time to arrive, depending on the size of your data. 🕒
        """
    )

    st.warning(
        """⚠️ Your data remains private and is automatically deleted after the analysis."""
    )

if connections:
    with zipfile.ZipFile(connections, "r") as zip_ref:
        zip_ref.extractall("files")  # Extract all the contents into the 'files' folder

    # Check if the 'followers.json' and 'following.json' files exist
    followers_path = "files/connections/followers_and_following/followers_1.json"
    following_path = "files/connections/followers_and_following/following.json"
    if not os.path.exists(followers_path) or not os.path.exists(following_path):
        st.error("Please make sure the ZIP file you uploaded is correct.")
        st.stop()
    else:
        st.success("ZIP file uploaded successfully.")

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

    # Sort alphabetically
    df_not_following_back = df_not_following_back.sort_values(
        by="username"
    ).reset_index(drop=True)

    st.subheader(str(len(df_not_following_back)) + " users/pages don't follow you back")
    st.dataframe(df_not_following_back, height=200)

    # Download CSV file
    st.markdown(
        "Save this file now and check for new unfollowers later (in a month for example). 🔄"
    )

    st.download_button(
        "Download the list",
        df_not_following_back.to_csv(index=False).encode("utf-8"),
        timestamp + "_not_following_back.csv",
        "text/csv",
    )

    # Compare with previous data
    previous_data = st.checkbox("I have the previous data to compare with.")
    if previous_data:
        previous_data = st.file_uploader(
            "Upload previous not following back data", type=["csv"], key="previous_data"
        )
        if previous_data:
            df_not_following_back_previous = pd.read_csv(previous_data)
            df_not_following_back_diff = df_not_following_back[
                ~df_not_following_back["username"].isin(
                    df_not_following_back_previous["username"]
                )
            ]

            # Sort alphabetically
            df_not_following_back_diff = df_not_following_back_diff.sort_values(
                by="username"
            )

            st.subheader(
                str(len(df_not_following_back_diff))
                + " newly detected Not Following Back users/pages"
            )
            # Display the difference if there is any
            if df_not_following_back_diff.empty:
                st.info("No new users detected! :smile:")
            else:
                st.dataframe(df_not_following_back_diff)

            # st.download_button(
            #     "Download the difference list",
            #     df_not_following_back_diff.to_csv(index=False).encode("utf-8"),
            #     timestamp + "_not_following_back_diff.csv",
            #     "text/csv",
            # )

    # Delete the files folder
    shutil.rmtree("files")

    # Clear cache
    st.cache_data.clear()
    st.cache_resource.clear()
