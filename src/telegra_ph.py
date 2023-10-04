import time
import requests
def publish2telegraph(access_token, title, srt):
    
    contents = split_srt(srt)    
# for short srt only one page 
    if len(contents)==1:
        return create_telegraph_page(access_token, title, contents[0])

# for long srt, generate multiple pages, 
    # 1.  first generate len(contents) empty pages
    page_urls=[]
    for i in range(len(contents)):
        url=create_telegraph_page(access_token, title, ["This is my first content page!"])
        page_urls.append( url )
    nav=generate_page_navigation(page_urls)

    # 2.  edit each page  for better navigation      
    print(page_urls)
    print("2.  edit each page  for better navigation     ")   
    for i in range(len(contents)):
        edit_telegraph_page(access_token, title, [nav] + contents[i], page_urls[i][18:])
        
    return page_urls[0]

def split_srt(srt):
    contents =  []
    content=[]
    for index, row in srt.iterrows():
        t0=time.gmtime( int(row['start']) )
        xx=time.strftime("%H:%M:%S", t0) +"\t"
        content.append({"tag":"p", "children":[xx+f"{row['text']}\n"]})
        str0=''.join(str(content))
        if len(str0.encode('utf-8'))>40*1000: # 40k bytes, equal not used, and not needed 
            contents.append(content)
            content=[]
    contents.append(content)

    return contents

# create a new page
def create_telegraph_page(access_token, title, content):
    base_url = "https://api.telegra.ph/createPage"
    params = {
        "access_token": access_token,  # 可选，如果你有一个
        "title": title,
        "content": content,
        "return_content": True
    }
    return post_telegraph_page(base_url, params)


# edit existing page
def edit_telegraph_page(access_token, title, content, path):
    base_url = "https://api.telegra.ph/editPage"   
    params = {
        "access_token": access_token,  # 可选，如果你有一个
        "title": title,
        "content": content,
        "path": path,  #  去除http://telegra.ph/后的路径
        "return_content": True
    }

    return post_telegraph_page(base_url, params)

##
def post_telegraph_page(base_url, params):
    json_response = requests.post(base_url, json=params).json()
    if json_response.get("ok"):
        return json_response["result"]["url"] 
    else:
        print("Error:", json_response.get("error"))
        print(f"Generate the 1th page url failed") 
        exit(1)
        return None

def generate_page_navigation(page_urls): 
    result={'tag':'p', 'children':["Page list:\t"]}
    for index,url in enumerate(page_urls):
        tt={
            'tag':'a', 
            'attrs':{'href':url}, 
            'children':[f"Page{index}"]
            }
        result['children'].append(tt)  
        result['children'].append('|')  

    return result

if __name__ == "__main__":

    import pandas as pd
    access_token="fa9614d3b779af58d2ced86451c1a00d81d24347f0b193b0fd1d0ad44ead"
    srt=pd.read_csv("d:/abc.csv")
    title="test"
    url=publish2telegraph(access_token,title , srt)
    print('url=', url)