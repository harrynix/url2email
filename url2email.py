import streamlit as st
import pandas as pd
import requests

# -----------------------------
# CONFIG
# -----------------------------
import streamlit as st
API_KEY = st.text_input("Enter your Apollo API key", type="password")
if not user_api_key:
    st.stop()




TARGET_TITLES = [
    "CEO",
    "Founder",
    "Owner",
    "Managing Director",
    "Marketing Director",
    "Co-Founder",
    "Director",
    "Sales Director",
    "Business Development Manager",
    "Commercial Director"
]

# -----------------------------
# LOGIC (converted from MATLAB)
# -----------------------------
def scan_websites(websites):
    results = []

    headers = {
        "Content-Type": "application/json",
        "x-Api-Key": API_KEY
    }

    for url in websites:
        url = url.strip()
        if not url:
            continue

        # Extract domain
        domain = url.replace("https://", "").replace("http://", "")
        domain = domain.replace("www.", "")
        domain = domain.split("/")[0]

        payload = {
            "q_organization_domains_list": [domain]
        }

        # First API call
        try:
            response = requests.post(
                "https://api.apollo.io/api/v1/mixed_people/api_search",
                json=payload,
                headers=headers,
                timeout=30
            ).json()
        except Exception as e:
            st.error(f"Error scanning {url}: {e}")
            continue

        people = response.get("people", [])

        for person in people:
            title = person.get("title", "")
            matched = any(t.lower() in title.lower() for t in TARGET_TITLES)

            if matched:
                entry = {
                    "Organisation": person.get("organization", {}).get("name", ""),
                    "FirstName": person.get("first_name", ""),
                    "LastName": "",
                    "Title": title,
                    "Phone": "",
                    "Email": ""
                }

                # If email exists, do second API call
                if person.get("has_email", False):
                    payload2 = {"id": person.get("id")}
                    try:
                        response2 = requests.post(
                            "https://api.apollo.io/api/v1/people/match",
                            json=payload2,
                            headers=headers,
                            timeout=30
                        ).json()
                        person2 = response2.get("person", {})
                        entry["LastName"] = person2.get("last_name", "")
                        entry["Email"] = person2.get("email", "")
                    except:
                        entry["LastName"] = person.get("last_name_obfuscated", "")
                        entry["Email"] = ""
                else:
                    entry["LastName"] = person.get("last_name_obfuscated", "")
                    entry["Email"] = ""

                results.append(entry)

    return pd.DataFrame(results)

# -----------------------------
# STREAMLIT UI
# -----------------------------
st.title("url2email v1")
st.write("Enter website URLs below (one per line).")

urls = st.text_area("Website URLs")

if st.button("Scan"):
    websites = urls.split("\n")
    df = scan_websites(websites)
    st.session_state["results"] = df

if "results" in st.session_state:
    st.subheader("Results")
    st.dataframe(st.session_state["results"])

    if st.button("Export"):
        st.session_state["results"].to_excel("Outreach_Data.xlsx", index=False)
        st.success("Exported Outreach_Data.xlsx")
