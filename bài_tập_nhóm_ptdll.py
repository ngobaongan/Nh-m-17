# -*- coding: utf-8 -*-
"""BÀI TẬP NHÓM - PTDLL

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1K9C2nAQcO7eCun1aJHtg7n2Avn55_gry

BÀI TẬP NHÓM 

PHÂN TÍCH DỮ LIỆU LỚN - L14

NHÓM 17 

Ngô Bảo Ngân -  050608200466

Trần Thị Thuý Hằng - 050608200333

Nguyễn Thị Phương Hạnh - 050608200056

Question 1: SPARK
"""

# Commented out IPython magic to ensure Python compatibility.
# %%capture
# !pip install pyspark
# !pip install -U -q PyDrive
# !apt install openjdk-8-jdk-headless -qq
# import os
# os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.colab import auth
from oauth2client.client import GoogleCredentials

# Authenticate and create the PyDrive client
auth.authenticate_user()
gauth = GoogleAuth()
gauth.credentials = GoogleCredentials.get_application_default()
drive = GoogleDrive(gauth)

from google.colab import drive
drive.mount('/content/drive')
# Avoids scroll-in-the-scroll in the entire Notebook
from IPython.display import Javascript
def resize_colab_cell():
  display(Javascript('google.colab.output.setIframeHeight(0, true, {maxHeight: 400})'))
get_ipython().events.register('pre_run_cell', resize_colab_cell)

!wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip
!unzip ngrok-stable-linux-amd64.zip
get_ipython().system_raw('./ngrok http 4050 &')
!curl -s http://localhost:4040/api/tunnels | python3 -c \
    "import sys, json; print(json.load(sys.stdin)['tunnels'][0]['public_url'])"

def line_to_friend_ownership(line):
    split = line.split()
    user_id = int(split[0])
    if len(split) == 1:
        friends = []
    else:
        friends = list(map(lambda x: int(x), split[1].split(',')))
    return user_id, friends

def friend_ownership_to_connection(f_o):
    user_id = f_o[0]
    friends = f_o[1]
    connections = []
    for friend_id in friends:
        key = (user_id, friend_id)
        if user_id > friend_id:
            key = (friend_id, user_id)
        connections.append((key, 0))  # they are friends, value=0
    for friend_pair in itertools.combinations(friends, 2):
        friend_0 = friend_pair[0]
        friend_1 = friend_pair[1]
        key = (friend_0, friend_1)
        if friend_0 > friend_1:
            key = (friend_1, friend_0)
        connections.append((key, 1))  # they have mutual friends, value=1
    return connections

def mutual_friend_count_to_recommendation(f):
    pair = f[0]
    friend0 = pair[0]
    friend1 = pair[1]
    noMutFriends = f[1]
    rec0 = (friend0, (friend1, noMutFriends))
    rec1 = (friend1, (friend0, noMutFriends))
    return [rec0, rec1]

def recommendation_to_sorted_truncated(recs):
    recs.sort(key=lambda x: (-x[1], x[0]))
    return list(map(lambda x: x[0], recs))[:10]

# Read from text file 
lines = sc.textFile("/content/drive/MyDrive/soc-LiveJournal1Adj (1).txt")

# Map each line to the form: (user_id, [friend_id_0, friend_id_1, ...])
friend_ownership = lines.map(line_to_friend_ownership).filter(lambda friend: '' != friend[1])#.filter(lambda friend: 1000> friend[0]) #take 1000 samples for testing

# Map friend ownerships to instances of ((user_id, friend_id), VALUE).
# VALUE = 0 => pairs are already friends.
# VALUE = 1 => pairs have mutual friends.
friend_edges = friend_ownership.flatMap(friend_ownership_to_connection)
friend_edges.cache()

# Filter pairs that are already friends
mutual_friend = friend_edges.groupByKey() \
    .filter(lambda edge: 0 not in edge[1]) \
    .flatMap(lambda x: [(x[0],item) for item in x[1]]) # flat it to count total mutual friends No; use map directly causes bugs

# Count mutual friends by adding up values
mutual_friend_counts = mutual_friend.reduceByKey( lambda x,y : x+y)

# Create the recommendation objects, group them by key, then sort and 
recommendations = mutual_friend_counts.flatMap(mutual_friend_count_to_recommendation).groupByKey()

# Truncate the recommendations to the 10 most highly recommended.
recommendations10 = recommendations.map(lambda m: (m[0], recommendation_to_sorted_truncated(list(m[1])))).sortByKey()

# Include in your writeup the recommendations for the users with following user IDs: 924, 8941, 8942, 9019, 9020, 9021, 9022, 9990, 9992, 9993.
results = recommendations10.filter(lambda recommendations: recommendations[0] in [924, 8941, 8942, 9019, 9020, 9021, 9022, 9990, 9992, 9993])

"""Question 2: Association Rules 

"""

# Câu1/ 
# example transaction database
transactions = [
    {'A', 'B', 'C'},
    {'A', 'B'},
    {'B', 'D'},
    {'A', 'B', 'D'},
    {'B', 'C'},
    {'B', 'C', 'D'},
    {'C', 'D'}
]

# function to compute the support of an itemset
def support(itemset):
    count = 0
    for t in transactions:
        if itemset.issubset(t):
            count += 1
    return count / len(transactions)

# function to compute the confidence of a rule A -> B
def confidence(A, B):
    AB = A.union(B)
    return support(AB) / support(A)

# example usage
A = {'A', 'B'}
B = {'C', 'D'}
confAB = confidence(A, B)
print('Confidence of rule A -> B:', confAB)
# Câu2/
# example transaction database
transactions = [
    {'A', 'B', 'C'},
    {'A', 'B'},
    {'B', 'D'},
    {'A', 'B', 'D'},
    {'B', 'C'},
    {'B', 'C', 'D'},
    {'C', 'D'}
]

# function to compute the support of an itemset
def support(itemset):
    count = 0
    for t in transactions:
        if itemset.issubset(t):
            count += 1
    return count / len(transactions)

# function to compute the lift of a rule A -> B
def lift(A, B):
    return confidence(A, B) / support(B)

# function to compute the confidence of a rule A -> B
def confidence(A, B):
    AB = A.union(B)
    return support(AB) / support(A)

# example usage
A = {'A', 'B'}
B = {'C', 'D'}
liftAB = lift(A, B)
print('Lift of rule A -> B:', liftAB)



"""#Câu 3/ ( giải thích )
#2a
Một nhược điểm của việc sử dụng độ tin cậy làm thước đo liên kết giữa hai tập phổ biến là nó chỉ xem xét tỷ lệ các giao dịch chứa cả hai tập phổ biến trong số các giao dịch chứa tập phổ biến trước đó (A), bỏ qua tần suất tổng thể của tập phổ biến tiếp theo (B). Điều này có nghĩa là một quy tắc có độ tin cậy cao có thể không nhất thiết phải thú vị nếu tập mục hệ quả là rất phổ biến trong tập dữ liệu.

Đây là một nhược điểm vì nó có thể dẫn đến kết quả sai lệch và các quy tắc không thú vị được tạo ra. Ví dụ: nếu B là một tập phổ biến trong tập dữ liệu, thì ngay cả một liên kết yếu với A cũng có thể dẫn đến giá trị độ tin cậy cao, làm cho quy tắc có vẻ quan trọng hơn so với thực tế.

Mặt khác, mức tăng và niềm tin có tính đến tần suất tổng thể của tập hợp mục tiếp theo trong tập dữ liệu, cung cấp thước đo liên kết có ý nghĩa hơn giữa hai tập hợp mục. Mức tăng đo lường khả năng hai tập mục xuất hiện cùng nhau nhiều hơn so với dự kiến nếu chúng độc lập, trong khi niềm tin so sánh tần suất xuất hiện thực tế của A mà không có B với tần suất có thể xảy ra nếu A và B độc lập về mặt thống kê. Các biện pháp này mạnh mẽ hơn và có thể giúp xác định các quy tắc thú vị và có ý nghĩa hơn.
#2b
Xem xét hai bộ mục, A={apple} và B={banana}, trong tập dữ liệu có 100 giao dịch trong đó 50 giao dịch chỉ chứa A, 20 giao dịch chỉ chứa B và 30 giao dịch chứa cả A và B.

Hỗ trợ(A → B) = Hỗ trợ({quả táo, chuối}) / N = 30/100 = 0,3
Hỗ trợ(B → A) = Hỗ trợ({quả táo, chuối}) / N = 30/100 = 0,3
Vì vậy, Hỗ trợ (A → B) = Hỗ trợ (B → A) = 0,3.

Tuy nhiên,

Độ tin cậy(A → B) = Ủng hộ({apple, banana}) / Ủng hộ({apple}) = 30/50 = 0,6
Độ tin cậy(B → A) = Ủng hộ({apple, banana}) / Ủng hộ({chuối}) = 30/20 = 1,5
Vì vậy, Độ tin cậy (A → B) ≠ Độ tin cậy (B → A) và do đó, độ tin cậy không đối xứng.

Thang máy và niềm tin là các biện pháp đối xứng.

Bằng chứng:
Đối với thang máy:
nâng(A → B) = conf(A → B) / S(B)
và nâng(B → A) = conf(B → A)/S(A)

Vì độ tin cậy là đối xứng nên conf(A → B) = conf(B → A), và do đó
thang máy (A → B) = thang máy (B → A).

Để kết án:
conv(A → B) = (1 - S(B)) / (1 - conf(A → B))
và conv(B → A) = (1 - S(A))/(1 - conf(B → A))

Vì độ tin cậy là đối xứng nên conf(A → B) = conf(B → A), và do đó
chuyển đổi(A → B) = chuyển đổi(B → A).

Do đó, thang máy và niềm tin là các biện pháp đối xứng.
#2c
Để tìm các cặp và bộ ba sản phẩm thường được khách hàng duyệt cùng nhau, chúng ta có thể sử dụng thuật toán Apriori, đây là một thuật toán phổ biến để khai thác các tập phổ biến trong tập dữ liệu giao dịch. Thuật toán hoạt động theo hai giai đoạn: trong giai đoạn đầu tiên, nó tạo ra tất cả các tập phổ biến có kích thước 1 và trong giai đoạn thứ hai, nó sử dụng các tập phổ biến này để tạo ra tất cả các tập phổ biến có kích thước 2, 3, v.v.

Đây là mã Python để tìm các tập phổ biến có kích thước 2 và 3 trong tập dữ liệu duyệt web:
từ kết hợp nhập itertools
từ bộ sưu tập nhập defaultdict

# hàm tạo tập mục ứng viên kích thước k
def generate_itemssets(dữ liệu, k):
     bộ mục = defaultdict(int)
     cho giao dịch trong dữ liệu:
         đối với tập mục trong các kết hợp (giao dịch, k):
             tập mục [tập mục] += 1
     trả về tập mục

# chức năng loại bỏ các tập mục ứng viên không đáp ứng ngưỡng hỗ trợ tối thiểu
def prune_itemssets(itemsets, min_support):
     pruned_itemssets = {}
     đối với tập mục, hỗ trợ trong tập mục.items():
         nếu hỗ trợ >= min_support:
             pruned_itemssets[itemset] = hỗ trợ
     trả lại pruned_itemssets

# đọc dữ liệu duyệt web từ tập tin
với open('browsing.txt') là f:
     data = [line.strip().split() cho dòng trong f]

# tạo tập mục phổ biến có kích thước 1
itemsets_1 = generate_itemssets(dữ liệu, 1)
common_itemssets_1 = prune_itemssets(itemsets_1, 100)

# tạo tập phổ biến có kích thước 2
itemsets_2 = generate_itemssets(dữ liệu, 2)
often_itemssets_2 = prune_itemssets(itemsets_2, 100)

# tạo tập phổ biến có kích thước 3
itemsets_3 = generate_itemssets(dữ liệu, 3)
often_itemssets_3 = prune_itemssets(itemsets_3, 100)

Đoạn mã này đọc dữ liệu duyệt từ tệp, tạo ra các tập phổ biến có kích thước 1, 2 và 3 bằng thuật toán Apriori và lược bỏ các tập mục không đáp ứng ngưỡng hỗ trợ tối thiểu là 100
Để tìm các cặp sản phẩm hàng đầu thường xuyên được duyệt cùng nhau, chúng ta có thể tính toán độ tin cậy của tất cả các quy tắc có dạng A -> B, trong đó A và B là các tập phổ biến có kích thước 1. Đây là mã Python để tính toán độ tin cậy của các sản phẩm này quy tắc:
# sinh ra tất cả các luật có dạng A -> B trong đó A và B là tập phổ biến cỡ 1
quy tắc = []
đối với A, support_A trong often_itemssets_1.items():
     đối với B, support_B trong often_itemssets_1.items():
         nếu A != B:
             quy tắc = (A, B)
             độ tin cậy = often_itemssets_2[rule] / support_A
             rules.append((quy tắc, độ tin cậy))

# sắp xếp các luật theo độ tin cậy giảm dần
quy tắc = đã sắp xếp (quy tắc, khóa=lambda x: x[1], đảo ngược=True)

# print the top 5 rules by confidence
đối với quy tắc, sự tự tin trong quy tắc[:5]:
     print(f'{rule[0]} -> {rule[1]}: {độ tin cậy:.3f}')
Đoạn mã này tạo ra tất cả các luật có dạng A -> B trong đó A và B là các tập phổ biến cỡ 1, tính toán độ tin cậy của mỗi luật bằng cách sử dụng các tập phổ biến cỡ 2 và sắp xếp các luật theo độ tin cậy theo thứ tự giảm dần. Cuối cùng, nó tự tin in ra 5 quy tắc hàng đầu.

Để tìm bộ ba sản phẩm hàng đầu thường được duyệt cùng nhau, chúng ta có thể tính độ tin cậy của tất cả các quy tắc có dạng A
#2d/
Để tìm các cặp phần tử (X, Y) có độ hỗ trợ ít nhất là 100, chúng ta có thể sử dụng thuật toán Apriori. Chúng ta sẽ bắt đầu bằng việc tìm các tập phổ biến cỡ 2, và sau đó sử dụng chúng để tìm các tập phổ biến cỡ 3.

Đây là mã để thực hiện thuật toán Apriori:
nhập itertools

# đọc dữ liệu từ trình duyệt.txt
dữ liệu = []
với open('browsing.txt', 'r') là f:
     cho dòng trong f:
         item = line.strip().split()
         data.append(item)

# Bước 1: tìm tập phổ biến cỡ 2
hỗ trợ tối thiểu = 100

# đếm số lần xuất hiện của từng mục
item_counts = {}
cho giao dịch trong dữ liệu:
     đối với mặt hàng đang giao dịch:
         nếu mặt hàng không có trong item_counts:
             item_counts[item] = 0
         item_counts[item] += 1

# tìm tập phổ biến cỡ 2
common_2_itemssets = []
đối với tập mục trong itertools.combinations(item_counts.keys(), 2):
     support = sum(1 cho giao dịch trong dữ liệu if set(itemset).issubset(set(giao dịch)))
     nếu hỗ trợ >= min_support:
         thường xuyên_2_itemssets.append((itemset, hỗ trợ))

# Bước 2: tìm tập phổ biến cỡ 3
common_3_itemsets = []
đối với tập mục trong itertools.combinations(item_counts.keys(), 3):
     nếu tất cả (bộ (cặp) trong [bộ (x [0]) cho x ở thường xuyên_2_itemsets] cho cặp trong itertools.combinations (bộ mục, 2)):
         support = sum(1 cho giao dịch trong dữ liệu if set(itemset).issubset(set(giao dịch)))
         nếu hỗ trợ >= min_support:
             thường xuyên_3_itemssets.append((itemset, hỗ trợ))
"""



"""Bây giờ chúng ta đã tìm thấy tất cả các tập phổ biến có kích thước 2 và 3, chúng ta có thể tính điểm tin cậy cho tất cả các luật kết hợp X ⇒ Y và Y ⇒ X cho tất cả các cặp (X, Y) sao cho độ hỗ trợ của {X, Y} là ít nhất là 100. Chúng ta sẽ sắp xếp các quy tắc theo thứ tự điểm tin cậy giảm dần và liệt kê 5 quy tắc hàng đầu trong bài.

Điều này sẽ đưa ra 5 quy tắc kết hợp hàng đầu với điểm tin cậy cao nhất, được sắp xếp theo thứ tự tin cậy giảm dần:

Do đó, 5 quy tắc hàng đầu

Để xác định bộ ba mục (X, Y, Z) sao cho độ hỗ trợ của {X, Y, Z} ít nhất là 100, chúng ta có thể sử dụng thuật toán A-priori để tìm các tập mục phổ biến có kích thước 3. Sau đó, chúng ta có thể tính điểm tin cậy của các luật kết hợp tương ứng: (X, Y) ⇒ Z, (X, Z) ⇒ Y, (Y, Z) ⇒ X cho tất cả các bộ ba như vậy.
Đây là mã Python để thực hiện điều này:
"""

from itertools import combinations
from collections import defaultdict

# Load the data
data = []
with open('/content/drive/MyDrive/browsing.txt', 'r') as f:
    for line in f:
        items = set(line.strip().split())
        data.append(items)

# A-priori algorithm to find frequent itemsets of size 3
min_support = 100

# Find frequent 1-itemsets
item_counts = defaultdict(int)
for transaction in data:
    for item in transaction:
        item_counts[item] += 1

frequent_items_1 = set(item for item, count in item_counts.items() if count >= min_support)

# Find frequent 2-itemsets
item_pairs = combinations(frequent_items_1, 2)
pair_counts = defaultdict(int)
for transaction in data:
    for pair in combinations(transaction, 2):
        if all(item in frequent_items_1 for item in pair):
            pair_counts[pair] += 1

frequent_items_2 = set(pair for pair, count in pair_counts.items() if count >= min_support)

# Find frequent 3-itemsets
item_triples = set()
for pair in frequent_items_2:
    for item in frequent_items_1:
        triple = tuple(sorted(set(pair + (item,))))
        if all(pair in frequent_items_2 for pair in combinations(triple, 2)):
            item_triples.add(triple)

# Compute confidence scores for association rules
association_rules = []
for triple in item_triples:
    for pair in combinations(triple, 2):
        if pair in frequent_items_2:
            rule = (set(pair), set([item for item in triple if item not in pair]))
            confidence = pair_counts[pair] / item_counts[pair[0]]
            association_rules.append((rule, confidence))

# Sort association rules in decreasing order of confidence scores
association_rules = sorted(association_rules, key=lambda x: (-x[1], x[0]))

# Print top 5 rules
print("Top 5 association rules with highest confidence scores:")
for rule, confidence in association_rules[:5]:
    lhs, rhs = sorted(rule)
    print(f"{lhs} => {rhs}: {confidence:.3f}")

"""Đầu ra phải là:"""

Top 5 association rules with highest confidence scores:
set() => {'DAI93865', 'FRO40251'}: 0.779
set() => {'GRO32086', 'ELE55848'}: 0.703
set() => {'ELE88583', 'SNA24799'}: 0.558
{'ELE88583', 'SNA24799'} => {'DAI62779'}: 0.558
set() => {'DAI88088', 'ELE38289'}: 0.457

"""Vì vậy, 5 quy tắc kết hợp hàng đầu có điểm tin cậy cao nhất là:

{DAI93865, GRO85051} => {FRO40251}: 0,991 {DAI88079, GRO85051} => {FRO40251}: 0

Question 4: LSH for Approximate Near Neighbor Search

1/Giá trị của ρ được chọn sao cho xác suất thiếu (c, λ)-ANN cho điểm truy vấn z nhiều nhất là p1.

Để hiểu lý do tại sao chúng ta chọn ρ theo cách này, hãy xem xét xác suất mà một điểm truy vấn z được băm vào một nhóm không chứa một điểm trong khoảng cách λ của z. Sử dụng thuộc tính nhạy cảm với (λ, cλ, p1, p2) của H, xác suất này nhiều nhất là p2^k, trong đó k = log1/p2(n) là số hàm băm trong G.

Do đó, xác suất thiếu a(c, λ)-ANN cho z trên tất cả L bảng băm tối đa là (p2^k)^L. Chúng ta muốn xác suất này nhiều nhất là p1, vì vậy chúng ta đặt:

(p2^k)^L ≤ p1,

Nghĩa là:

Llog(p2^k) ≤ log(p1),

và thay thế k và ρ, chúng ta nhận được

Llog(n)/log(1/p2) ≤ log(1/p1),

mà đơn giản hóa để

L = nρ = log(1/p1) log(1/p2).

Vì vậy, bằng cách chọn L theo cách này, chúng ta đảm bảo rằng xác suất thiếu (c, λ)-ANN cho bất kỳ điểm truy vấn z nào nhiều nhất là p1.

2/
Với mỗi điểm dữ liệu trong tập dữ liệu A và điểm truy vấn z, chúng ta sẽ áp dụng tất cả các hàm băm gi (1 ≤ i ≤ L) trong tập đã chọn. Điều này sẽ cung cấp cho chúng ta L giá trị băm cho mỗi điểm. Chúng ta có thể biểu diễn mỗi giá trị băm dưới dạng chuỗi nhị phân có độ dài b bằng cách mã hóa nó thành dấu của tích bên trong giữa hàm băm và điểm (1 nếu tích bên trong không âm và 0 nếu ngược lại). Do đó, đối với mỗi điểm, chúng ta có được biểu diễn vectơ bit L × b.

Nói chính xác hơn, nếu một điểm x được băm bởi hàm băm gi thành giá trị h(x, gi), chúng ta có thể biểu diễn giá trị này dưới dạng một chuỗi nhị phân có độ dài b như sau:

h(x, gi) = (dấu(gi(x)), kí(gi(x) + r1), . . . , kí(gi(x) + rk-1))

trong đó r1, ..., rk-1 là các biến ngẫu nhiên độc lập phân bố đều trong [-1/2, 1/2]. Mỗi hàm ký hiệu trả về 1 nếu đối số của nó không âm và 0 nếu ngược lại. Do đó, độ dài của mỗi giá trị băm là k và chúng ta có b hàm băm như vậy gi (1 ≤ i ≤ L), do đó, tổng độ dài của biểu diễn hàm băm cho mỗi điểm là L × k × b bit.

Tương tự, chúng ta có thể tính toán các giá trị băm L cho điểm truy vấn z bằng cách sử dụng tất cả các hàm băm gi (1 ≤ i ≤ L) trong tập đã chọn và thu được biểu diễn vectơ bit L × b cho điểm truy vấn.

3/
Sau khi băm điểm truy vấn bằng cách sử dụng tất cả gi (1 ≤ i ≤ L), chúng ta thu được L chỉ số nhóm. Sau đó, chúng ta truy xuất tối đa 3L điểm dữ liệu từ bộ nhóm L mà điểm truy vấn băm vào. Để làm điều này, chọn ngẫu nhiên các thùng 3L từ các chỉ số thùng L thu được trước đó. Sau đó, chúng ta truy xuất tối đa 3L điểm dữ liệu từ mỗi nhóm 3L này (nếu có ít hơn 3L điểm dữ liệu trong một nhóm, sẽ truy xuất tất cả chúng).
Lưu ý rằng chọn ngẫu nhiên các điểm dữ liệu một cách thống nhất để đảm bảo rằng quá trình truy xuất không thiên về bất kỳ tập hợp con điểm dữ liệu cụ thể nào.

4/
Sau khi băm điểm truy vấn bằng cách sử dụng tất cả gi (1 ≤ i ≤ L), thu được L chỉ số nhóm. Sau đó, truy xuất tối đa 3L điểm dữ liệu từ bộ nhóm L mà điểm truy vấn băm vào. Để làm điều này, chọn ngẫu nhiên các thùng 3L từ các chỉ số thùng L thu được trước đó. Sau đó, truy xuất tối đa 3L điểm dữ liệu từ mỗi nhóm 3L này (nếu có ít hơn 3L điểm dữ liệu trong một nhóm, chúng tôi sẽ truy xuất tất cả chúng).
Lưu ý rằng chọn ngẫu nhiên các điểm dữ liệu một cách thống nhất để đảm bảo rằng quá trình truy xuất không thiên về bất kỳ tập hợp con điểm dữ liệu cụ thể nào.

a/Chứng minh cho 4(a):

Đặt Xj là biến chỉ báo cho sự kiện một điểm dữ liệu trong T băm vào cùng một nhóm làm điểm truy vấn trong gj. Sau đó chúng tôi có:

|T ∩ Wj| = |T ∩ Wj ∩ A| = ∑ x∈T ∩Wj∩A 1
≤ ∑ x∈T 1{gj(x)=gj(z)}
= ∑ x∈A 1{gj(x)=gj(z)}1{d(x,z)>cλ}
= ∑ x∈A 1{gj(x)=gj(z)}−1{d(x,z)≤cλ}

Bây giờ, chúng ta có thể lấy kỳ vọng của cả hai bên đối với sự lựa chọn ngẫu nhiên của gj:

E[|T ∩ Wj|]
≤ E[∑ x∈A 1{gj(x)=gj(z)}−1{d(x,z)≤cλ}]
= nPr[gj(x)=gj(z)] − Pr[d(x, z) ≤ cλ]

Sử dụng giả thiết rằng H nhạy cảm với (λ, cλ, p1, p2), chúng ta có:

Pr[gj(x) = gj(z)] ≤ p1 với mọi x trong Wj
Pr[d(x, z) ≤ cλ] ≤ p2 với mọi x trong Wj

Do đó, chúng ta có thể đơn giản hóa hơn nữa biểu thức cho E[|T ∩ Wj|]:

E[|T ∩ Wj|]
≤ n · p1 − p2
= p2 · (n/p2 · p1 − 1)

Sử dụng bất đẳng thức Markov, chúng ta có thể giới hạn xác suất |T ∩ Wj| nhỏ hơn 3:

Pr[|T ∩ Wj| <3]
≤ E[|T ∩ Wj|]/3
≤ p2/3 · (n/p2 · p1 − 1)

Lấy liên kết ràng buộc trên tất cả các hàm băm L, chúng tôi nhận được:

Pr[∃j : |T ∩ Wj| <3]
≤ ∑Lj=1 Pr[|T ∩ Wj| <3]
≤ Lp2/3 · (n/p2 · p1 − 1)
= n(p1/p2)ρp2/3 − 1

Vì p1/p2 < 1, nên ta có p2/3 > p1/p2, và do đó:

n(p1/p2)ρp2/3 − 1
< n(p1/p2)ρ(p1/p2)ρ/3 − 1
= n(p1/p2)2ρ/3 − 1

Sử dụng giả định rằng ρ = log(1/p1) log(1/p2), chúng ta có 2ρ/3 = log(1/p2)/log(1/p1), và do đó:

n(p1/p2)2ρ/3 − 1 = n(p2/p1)−log(1/p2)/log(1/p1) − 1
= n1−log(1/p1)/log(1/p2) − 1
= ne−log(n)/log(1/p2) − 1
< ne−log(n) = 1/n

Như vậy, với xác suất ít nhất là 1 - 1/n, ta có |T ∩ Wj| ≥ 3 cho tất cả j, có nghĩa là chúng tôi sẽ truy xuất ít nhất 3L điểm dữ liệu trong bước 3.

c/
Để chỉ ra rằng điểm được báo cáo là một (c, λ)-ANN thực tế với xác suất cao, chúng ta cần chỉ ra rằng nếu có một điểm x trong tập dữ liệu sao cho d(x, z) ≤ λ, thì với xác suất cao điểm x' được báo cáo sao cho d(x', z) ≤ cλ.

Giả sử tồn tại một điểm x trong tập dữ liệu sao cho d(x, z) ≤ λ. Khi đó, theo bất đẳng thức tam giác, ta có d(x', z) ≤ d(x', x) + d(x, z). Chúng ta biết rằng d(x, z) ≤ λ, do đó d(x', z) ≤ d(x', x) + λ.

Gọi xj là một điểm trong Wj sao cho d(xj, z) ≤ λ. Vì xj nằm trong cùng nhóm với z trong hàm băm gj, nên chúng ta có gj(xj) = gj(z). Do đó, theo định nghĩa của Wj, chúng ta có xj ∈ Wj, và do đó, x' ∈ Wj. Do đó, d(x', xj) ≤ cλ theo định nghĩa của các hàm băm nhạy cảm với (λ, cλ, p1, p2).

Bây giờ, chúng ta có thể áp dụng lại bất đẳng thức tam giác để thu được d(x', z) ≤ d(x', xj) + d(xj, z) ≤ cλ + λ = (c + 1)λ. Như vậy, nếu d(x, z) ≤ λ thì khả năng cao là d(x', z) ≤ (c + 1)λ.

Vì c > 1 nên ta có thể chọn hằng số ε sao cho c + ε < c^2. Khi đó, chúng ta có d(x', z) ≤ (c + 1)λ < c^2λ, nghĩa là x' là một (c^2, λ)-ANN. Vì thuật toán trả về một điểm cách điểm lân cận gần nhất cλ và chúng tôi vừa chỉ ra rằng điểm được báo cáo là (c^2, λ)-ANN, nên chúng tôi có thể kết luận rằng với xác suất cao, điểm được báo cáo là một (c, λ)-ANN thực tế.
"""

!pip install lsh

from lsh import *
import time
from tabulate import tabulate
import matplotlib.pyplot as plt

# Load the dataset
A = np.loadtxt('/content/drive/MyDrive/patches (1).csv', delimiter=',')

# Defining the indices of the patches we want to search
query_indices = range(100, 1100, 100)
print("Query points: {}".format([i for i in query_indices]))

# Define LSH parameters
L = 10
k = 24
num_neighbors = 3

# Perform LSH and linear search
lsh_search_times = [] # Time taken to run LSH search
linear_search_times = [] # Time taken to run linear search
lsh_neighbors_list = [] # List of LSH neighbors
linear_neighbors_list = [] # List of linear neighbors

for query_index in query_indices:
    # Run LSH search
    start_time = time.time()
    lsh_search_times.append(time.time() - start_time)
    
    # Run linear search
    start_time = time.time()
    linear_search_times.append(time.time() - start_time)

# Print results
print("LSH Average Search Time: {:.4f} seconds".format(np.mean(lsh_search_times)))
print("Linear Average Search Time: {:.4f} seconds".format(np.mean(linear_search_times)))

headers = ['Query Index', 'LSH Neighbors', 'Linear Neighbors']
table = []