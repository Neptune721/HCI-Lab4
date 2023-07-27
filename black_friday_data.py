import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(external_stylesheets=external_stylesheets)
# 导入数据
df = pd.read_csv("lab4-datasets/black-friday/BlackFriday.csv")


# 为了保证原始数据的不动copy一份源数据
# 并且希望得到一张新的表 记录5819位消费者的信息
UserInfo = df.copy()
UserInfo = UserInfo.pivot_table(
    index=['User_ID', 'Gender', 'Age', 'Occupation', 'City_Category', 'Stay_In_Current_City_Years', \
           'Marital_Status'], values=['Purchase'], aggfunc='sum').reset_index()
UserInfo.nunique()
colors = ['salmon', 'lightskyblue', '#FFF68F', 'palegreen', 'lightpink', 'silver', 'burlywood', 'plum', 'rosybrown']
UserInfo['Number'] = 1
feature_class = UserInfo.groupby('Gender')[['Purchase', 'Number']].sum().sort_values('Purchase', ascending=False)


# fig = px.sunburst(feature_class.reset_index(), path=["Gender", "Purchase"], values="Purchase",hover_data=["Number"])

# 根据分类把userInfo进行分类
def feature_group(data, group, text):  # data:数据集，group:要分类的字段
    feature_class = data.groupby(group)[['Purchase', 'Number']].sum().sort_values('Purchase', ascending=False)
    feature_class.info()
    inner_fig = px.sunburst(feature_class.reset_index(), path=[group, "Purchase"], values="Purchase",
                            hover_data=["Number"])
    # 添加标题
    inner_fig.update_layout(title=text + "消费额与消费数量对比")
    # 添加注释
    inner_fig.add_annotation(text="备注：这里是一些说明。内圈是属性，外圈是消费总金额，鼠标悬停可查看人数", xref="paper",
                             yref="paper", x=0.5, y=-0.1, showarrow=False)

    return inner_fig


fig = feature_group(UserInfo, 'Age', '年龄')


# 定义回调函数
@app.callback(
    dash.dependencies.Output("example-graph-2", "figure"),
    [dash.dependencies.Input("dropdown", "value")]
)
def update_figure(value):
    # # 根据单选下拉框的值更新图形的颜色属性
    # fig.update_traces(marker=dict(colors=value))
    if (value == None):
        return feature_group(UserInfo, 'Age', '年龄')
    fig = feature_group(UserInfo, value, value)
    return fig


# 定义回调函数
@app.callback(
    dash.dependencies.Output("myfig-2", "figure"),
    [dash.dependencies.Input("dropdown2", "value")]
)
def update_figure2(value):
    # # 根据单选下拉框的值更新图形的颜色属性
    # fig.update_traces(marker=dict(colors=value))
    if value == "sum":
        return fig2
        # return px.pie(Category_Group, values=Category_Group.values, names=Category_Group.index)
    elif value == "box":
        return fig4
        # return px.box(df,
        #               x="Product_Category_1",
        #               y="Purchase",
        #               color="Product_Category_1")
    elif value == "sex":
        return fig3
        # px.bar(Category_Gender_pct, x=Category_Gender_pct.index, y=["F", "M"], barmode="group")
    else:
        return fig2
        # return px.pie(Category_Group, values=Category_Group.values, names=Category_Group.index)


# 分析商品

# 因为Product_Category_2、Product_Category_3缺失值太多，暂不分析，只对Product_Category_1（类别1）进行分析
# 分析一下类别1各个类别的销售额
Category_Group = round(df.groupby('Product_Category_1').Purchase.sum().sort_values(ascending=False) / 10000000, 1)
Category_Group.info()
fig2 = px.pie(Category_Group, values=Category_Group.values, names=Category_Group.index)

# 结合商品类别和消费者性别进行分析，看一看男性和女性消费者的消费偏好
Category_Gender_pvt = pd.pivot_table(df, index='Product_Category_1', columns='Gender',
                                     values='Purchase', aggfunc=np.sum)
# 计算每个商品类别中，男女各自所占的百分比
Category_Gender_pct = Category_Gender_pvt.div(Category_Gender_pvt.sum(axis=1), axis=0).mul(100)

fig3 = px.bar(Category_Gender_pct, x=Category_Gender_pct.index, y=["F", "M"], barmode="group")

# test
# df_cpy4 = df.query("Product_Category_1 == 1")
# df_cpy4["bin_Purchase"] = pd.cut(df_cpy4["Purchase"], bins=10)
# fig4 = px.scatter(df_cpy4, x="bin_Purchase", color="Gender", hover_name="User_ID")

fig4 = px.box(df,
              x="Product_Category_1",
              y="Purchase",
              color="Product_Category_1")

fig5=fig2


# 销售额Top20商品
df_cpy3 = df.groupby(["Product_ID"]).agg({"Purchase": "sum"}).reset_index()
# 改成以万为单位
df_cpy3["Purchase"] = df_cpy3["Purchase"].apply(lambda x: round(x / 10000, 2))

# 销售额降序
df_cpy3.sort_values("Purchase", ascending=False, inplace=True)

fig6 = px.bar(df_cpy3[:20],  # 选择前10
             x="Product_ID",
             y="Purchase",
             color="Purchase",
             text="Purchase")

fig6.update_layout(title="Top20商品销售额的对比图(单位：万)")


app.layout = html.Div(
    children=[
        html.H1(
            children='BlackFriday Dash',
            style={
                'textAlign': 'center'
            }
        ),

        # 创建一个包含两个子Div的Div，作为上方的行
        html.Div([
            # 创建一个包含图形组件的Div，作为左上方的列
            html.Div([
                dcc.Markdown(
                    id="text1",
                    children="显示销售额与销售数量跟这些因素之间的关系。在下面的单选框里选择不同值以改变显示",
                    # 设置卡片样式和阴影效果
                    style={
                        "border": "1px solid #ddd",
                        "border-radius": "5px",
                        "padding": "10px",
                        "box-shadow": "2px 2px 2px lightgrey"
                    }
                ),
                # 添加单选框组件
                dcc.Dropdown(
                    id="dropdown",
                    options=[
                        {"label": "Gender", "value": "Gender"},
                        {"label": "Age", "value": "Age"},
                        {"label": "Occupation", "value": "Occupation"},
                        {"label": "Stay_In_Current_City_Years", "value": "Stay_In_Current_City_Years"},
                    ],
                    value="Gender",
                    clearable=False  # 禁止清除选择的值
                ),
                dcc.Graph(
                    id='example-graph-2',
                    figure=fig  # 饼图
                ),
            ], className="six columns"),  # 使用six columns类来指定宽度为一半
            # 创建一个包含图形组件的Div，作为右上方的列
            html.Div([
                dcc.Markdown(
                    id="text2",
                    children="下面是展示不同商品品类的销售金额与男女比例。在下面的单选框里选择不同值以改变显示",
                    # 设置卡片样式和阴影效果
                    style={
                        "border": "1px solid #ddd",
                        "border-radius": "5px",
                        "padding": "10px",
                        "box-shadow": "2px 2px 2px lightgrey"
                    }
                ),
                # 添加单选框组件
                dcc.Dropdown(
                    id="dropdown2",
                    options=[
                        {"label": "sum-各商品品类销售总额，单位是10000000（百万美元）", "value": "sum"},
                        {"label": "box-各商品品类与销售额图", "value": "box"},
                        {"label": "sex-各商品品类消费的男女比例", "value": "sex"},
                    ],
                    value="sum",
                    clearable=False  # 禁止清除选择的值
                ),
                dcc.Graph(
                    id='myfig-2',
                    figure=fig5  # 饼图
                ),
            ], className="six columns"),  # 使用six columns类来指定宽度为一半
        ], className="row"),  # 使用row类来指定布局为水平排

        # 创建一个包含图形组件的Div，作为左上方的列
        html.Div([
            dcc.Markdown(
                id="text5",
                children="显示top20商品销售额",
                # 设置卡片样式和阴影效果
                style={
                    "border": "1px solid #ddd",
                    "border-radius": "5px",
                    "padding": "10px",
                    "box-shadow": "2px 2px 2px lightgrey"
                }
            ),

            dcc.Graph(
                id='fig-6',
                figure=fig6  # top20
            ),
        ], className="row"),

    ], className="row twelve columns")

if __name__ == '__main__':
    app.run_server(debug=True)
