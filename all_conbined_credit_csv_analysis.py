"""
クレジットカードの利用額の推移を分析するクラス.
支払いが完了していない月はcsvのタイトル以外はヘッダーが構築されないらしく, これにも対応できるように調整する必要がある.
年間合計利用額と月平均利用額出さないとだめじゃん.
"""
import csv, os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
# matplotlibのフォントキャッシュを削除．
# matplotlib.font_manager._rebuild()
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import FuncFormatter
PATH_TO_CSV_DIR = "yearly_credit_csvs"

class Yearly_Credit_Analysis:
    def __init__(self, dir=PATH_TO_CSV_DIR):
        # この段階からデータを読み込んでクラス変数として保持した方がいいよな.
        csv_files = [f for f in os.listdir(dir) if f.endswith('.csv')]
        # indexの設定.
        # 今回の場合はindex=0がAmexCsvのご利用日に相当.
        self.date_column = 0
        # ご利用内容．
        self.category_column = 2
        # 会員番号
        self.membership_number = 4
        # 利用金額.
        self.value_column = 5
        # DFの初期化.
        self.all_data = pd.DataFrame()
        # 雑費の内訳が重要であることがわかったので，雑費のインデックスを持つようにする.
        self.misc_categories = None
        for file in csv_files:
            # ヘッダー部分の行は削除する．skiprowsはいらないよな．
            df = pd.read_csv(os.path.join(dir, file), header=None, skiprows=1, usecols=[self.date_column, self.value_column, self.category_column, self.membership_number], encoding='shift_jis')
            #print(f"now df is {df}")
            # csvでは全てがデフォルトで文字列で記録されているので, 金額部分をstrからintに変換.
            # ここでNaNが発生してる．なんで？ → カンマが入ってたからや．変換まえに削除しないと．
            df[self.value_column] = df[self.value_column].str.replace(',', '', regex=False)
            df[self.value_column] = pd.to_numeric(df[self.value_column], errors='coerce')
            #print(f"now str to int df = {df}")
            # Nanを含む行を削除する.
            df.dropna(subset=[self.value_column], inplace=True)
            # さらに，負の値も削除する.
            df = df[df[self.value_column] >= 0]
            self.all_data = pd.concat([self.all_data, df])
        # 最後に日付列のデータ型をdatetimeに変換する. データ分析をやりやすくするため.
        self.all_data[self.date_column] = pd.to_datetime(self.all_data[self.date_column])
        print(f"self.all_data = \n{self.all_data}")
        # フォントパスの設定.
        self.font_path = 'ipaexg.ttf'
        self.font_prop = FontProperties(fname=self.font_path, size=12)
        print(f"Loaded font: {self.font_prop.get_name()}")

        # matplotlibのフォント設定を更新.
        plt.rcParams['font.family'] = self.font_prop.get_name()
    

    # フォントテスト用メソッド．
    def font_example_plot(self):
        plt.figure(figsize=(8, 6))
        plt.plot([1, 2, 3], [4, 5, 6], label='データ')
        plt.title('タイトル', fontproperties=self.font_prop)
        plt.xlabel('X軸', fontproperties=self.font_prop)
        plt.ylabel('Y軸', fontproperties=self.font_prop)
        plt.legend(prop=self.font_prop)
        plt.show()

    # 年毎のカード利用額推移をプロット. 円グラフも追加したいな.
    def plot_yearly_credit_usage(self):
        # まずself.all_datasから自動的にカテゴリを抽出.
        unique_categories = self.all_data[self.category_column].unique()

        # 月毎にデータを集計
        monthly_data = self.all_data.groupby(self.all_data[self.date_column].dt.to_period('M'))[self.value_column].sum()
        #print(f"monthly_data = \n{monthly_data}") # ← Pandas Seriesというデータ型.

        # インデックスをdatetime型に戻す
        monthly_data.index = monthly_data.index.to_timestamp()
        #print(f"monthly_data = \n{monthly_data}") # ← Pandas Seriesというデータ型.

        # 単位をK単位に変換する.
        # 10K(万)単位に変更
        monthly_data_transformed = monthly_data.apply(lambda x: x / 10000)

        # 日付形式を変更する.今回は%mにする. 年は2023に固定されているので表示する必要はない.
        monthly_data_transformed.index = monthly_data_transformed.index.strftime('%m')
        #print(f"monthly_data_transformed = {monthly_data_transformed}")

        #ig, (ax1, ax2, ax3, ax4) = plt.subplots(2, 2, figsize=(24, 6))
        fig, axes = plt.subplots(2, 2, figsize=(20, 12))
        ax1, ax2, ax3, ax4 = axes.flatten()
        #print(f"monthly_datta_transformed.index = {monthly_data_transformed.index}")

        # 棒グラフの描画
        ax1.bar(monthly_data_transformed.index, monthly_data_transformed, color='skyblue', label='bar', width = 0.5)

        # 折れ線グラフの描画
        ax1.plot(monthly_data_transformed.index, monthly_data_transformed, color='orange', label = 'line')

        # 軸とタイトルの設定
        ax1.set_title('Monthly Credit Used Trend', fontproperties=self.font_prop)
        ax1.set_xlabel('Month(2023)', fontproperties=self.font_prop)
        ax1.set_ylabel('Amount Used (Thousands-Yen)', fontproperties=self.font_prop)
        # 判例の表示.
        ax1.legend()

        # 円グラフのデータ準備(年間全体の各月の支出割合を算出する)
        # pie_data = monthly_data_transformed.groupby(monthly_data_transformed.index).sum()
        # pie_data = monthly_data_transformed.iloc[monthly_data_transformed > 0].groupby(monthly_data_transformed.index).sum()
        pie_data = monthly_data_transformed.loc[monthly_data_transformed > 0].groupby(monthly_data_transformed.index).sum()

        colors = plt.cm.Paired(range(len(pie_data)))

        # # 年間の月単位の支出円グラフの描画
        ax2.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', colors=colors)
        ax2.set_title('Percentage of Monthly Spending', fontproperties=self.font_prop)

        # カテゴリごとの年間支出を計算.
        category_spending = self.all_data.groupby(self.category_column)[self.value_column].sum()
        total_spending = category_spending.sum()
        category_spending_percentage = category_spending.apply(lambda x: (x / total_spending) * 100)

        # 5%未満のカテゴリを雑費に統合.
        misc_spending = category_spending_percentage[category_spending_percentage < 5].sum()
        category_spending_percentage = category_spending_percentage[category_spending_percentage >= 5]
        # print(f"category_spending_percentage = {category_spending_percentage}")
        category_spending_percentage['雑費'] = misc_spending
        print(f"category_spending_percentage['雑費'] = {category_spending_percentage['雑費']}")

        # # カテゴリ毎の年間収支割合の円グラフの描画.
        ax3.pie(category_spending_percentage, labels=category_spending_percentage.index, autopct='%1.1f%%', colors=plt.cm.Paired(range(len(category_spending_percentage))), textprops={'fontproperties': self.font_prop})
        ax3.set_title('Annual Spending by Category', fontproperties=self.font_prop)


        # 各カテゴリの年間合計支出を計算
        category_total_spending = self.all_data.groupby(self.category_column)[self.value_column].sum()

        # 全体の合計支出を計算
        total_spending = category_total_spending.sum()

        # 各カテゴリの支出割合を計算
        category_spending_percentage = category_total_spending.apply(lambda x: x / total_spending * 100)

        # 5%未満のカテゴリを特定
        small_categories = category_spending_percentage[category_spending_percentage < 5].index
        # small_categoriesには全体の5%未満のvalueを持つインデックスが入ってる．
        # print(f"small_categories = {small_categories}")
        # 雑費のインデックスをクラスインスタンスとして保持するようにする．
        self.misc_categories = small_categories

        # 5%未満のカテゴリに該当するデータを集計
        misc_categories_spending = self.all_data[self.all_data[self.category_column].isin(small_categories)]

        # ここは合計金額の割合か？
        misc_categories_total = misc_categories_spending.groupby(self.category_column)[self.value_column].sum()

        # 雑費の内訳の円グラフの描画
        ax4.pie(misc_categories_total, labels=misc_categories_total.index, autopct='%1.1f%%', colors=plt.cm.Paired(range(len(misc_categories_total))), textprops={'fontproperties': self.font_prop})
        ax4.set_title('Breakdown of Miscellaneous Spending', fontproperties=self.font_prop)

        # グラフの表示.
        plt.tight_layout()
        # 一旦コメントアウト. → 次に呼び出されるメソッドplot_misc_spending_analysis()で全て一気に表示される.
        #   → これは何故かというと，plt自体は共通しているため.
        # plt.show()

    # 先にplot_yearly_credit_usage()メソッドを実行しなくてはならないのが難点...
    def plot_misc_spending_analysis(self):
        # self.misc_categoriesを参照し，self.all_datasの該当インデックスのみから円グラフをプロット．
        # 上位20のカテゴリーと，残りはOthersとして円グラフをプロットする.
        # 雑費カテゴリーに分類されるものを抽出.
        misc_categories_spending =  self.all_data[self.all_data[self.category_column].isin(self.misc_categories)]
        # 合計金額を算出.
        misc_categories_total = misc_categories_spending.groupby(self.category_column)[self.value_column].sum()
        # 上位20のカテゴリーと残りをOthersとして分類
        misc_categories_sorted = misc_categories_total.sort_values(ascending=False)
        top_20_categories = misc_categories_sorted[:20]
        others = misc_categories_sorted[20:].sum()
        
        # データを準備
        labels = list(top_20_categories.index) + ['Others']
        values = list(top_20_categories.values) + [others]
        
        # 円グラフのプロット
        colors = plt.cm.Paired(range(len(labels)))
        plt.figure(figsize=(12, 6))
        plt.pie(values, labels=labels, autopct='%1.1f%%', colors=colors, textprops={'fontproperties': self.font_prop})
        plt.title('Breakdown of Miscellaneous Spending (Top 20 + Others)', fontproperties=self.font_prop)
        plt.show()

if __name__=="__main__":
    # 初期化．
    ca = Yearly_Credit_Analysis()
    # フォントのテスト.
    #ca.font_example_plot()
    ca.plot_yearly_credit_usage()
    ca.plot_misc_spending_analysis()