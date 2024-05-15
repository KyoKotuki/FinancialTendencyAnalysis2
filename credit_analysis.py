"""
クレジットカードの利用額の推移を分析するクラス.
支払いが完了していない月はcsvのタイトル以外はヘッダーが構築されないらしく, これにも対応できるように調整する必要がある.
年間合計利用額と月平均利用額出さないとだめじゃん.
"""
import csv, os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import FuncFormatter
PATH_TO_CSV_DIR = "credit_csvs"

class Credit_Analysis:
    def __init__(self, directory=PATH_TO_CSV_DIR):
        # この段階からデータを読み込んでクラス変数として保持した方がいいよな.
        csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
        # indexの設定.
        self.date_colum = 0
        self.categorycolumn = 1
        self.valuecolumn = 2
        # DFの初期化.
        self.all_data = pd.DataFrame()
        for file in csv_files:
            df = pd.read_csv(os.path.join(directory, file), header=None, skiprows=2, usecols=[self.date_colum, self.valuecolumn, self.categorycolumn], encoding='shift_jis')
            # csvでは全てがデフォルトで文字列で記録されているので, 金額部分をstrからintに変換.
            df[self.valuecolumn] = pd.to_numeric(df[self.valuecolumn], errors='coerce')
            # Nanを含む行を削除する.
            df.dropna(subset=[self.valuecolumn], inplace=True)
            self.all_data = pd.concat([self.all_data, df])
        # 最後に日付列のデータ型をdatetimeに変換する. データ分析をやりやすくするため.
        self.all_data[self.date_colum] = pd.to_datetime(self.all_data[self.date_colum])
        print(f"self.all_data = \n{self.all_data}")
        # フォントパスの設定.
        self.font_path = 'ipaexg.ttf'
        self.font_prop = FontProperties(fname=self.font_path, size=12)

        # matplotlibのフォント設定を更新.
        plt.rcParams['font.family'] = self.font_prop.get_name()
    
    # 月指定で積み上げグラフを表示する, んだけど20%以上を占めるカテゴリのみを表示にしないと見ずらくて分析に向かないかもしれん.
    def get_category_and_plot_credit_spending(self):
        """
        自動的にcsvからカテゴリーを抽出し, 各カテゴリーの月ごとの利用額・年毎の利用額を出力する.
        まずは月毎の出力のみやるか.
        月毎の出力には積み上げグラフが一番見やすいよな.
        """
        # まずself.all_datasから自動的にカテゴリを抽出すればいいか.
        unique_categories = self.all_data[self.categorycolumn].unique()
        # print(f'unique_categories = \n{unique_categories}')

        # ユーザーから表示したい月を入力させる
        selected_month = input("表示したい月を YYYY-MM 形式で入力してください (例:2023-01) :")

        # カテゴリ毎の月単位合計利用金額を見る.
        monthly_sum_per_category = {}

        for category in unique_categories:
            category_data = self.all_data[self.all_data[self.categorycolumn] == category]
            monthly_sum = category_data.groupby(category_data[self.date_colum].dt.to_period('M'))[self.valuecolumn].sum()
            monthly_sum_per_category[category] = monthly_sum
        
        # 月毎の積み上げデータを作成
        monthly_stacked_data = pd.DataFrame()

        for category, data in monthly_sum_per_category.items():
            if selected_month in data.index:
                monthly_stacked_data[category] = [data[selected_month]]
            else:
                monthly_stacked_data[category] = [0]

        # グラフの描画. x軸の各値の日本語表示ができてないな. しかも表示斜めだったし.
        # 積み上げグラフの作成.
        monthly_stacked_data.plot(kind='bar', stacked=True)
        plt.title("月毎のカテゴリ別利用額推移", fontproperties=self.font_prop)
        plt.xlabel('月', fontproperties=self.font_prop)
        plt.ylabel('利用額', fontproperties=self.font_prop)
        #plt.legend(title='カテゴリ')
        plt.show()
    
    # 月毎の支出のカテゴリごとの割合を円グラフでプロットする.
    def plot_category_spending_pie(self):
        # まずself.all_datasから自動的にカテゴリを抽出すればいいか.
        unique_categories = self.all_data[self.categorycolumn].unique()
        # print(f'unique_categories = \n{unique_categories}')

        # ユーザーから表示したい月を入力させる
        selected_month = input("表示したい月を YYYY-MM 形式で入力してください (例:2023-01) :")

        # カテゴリ毎の月単位合計利用金額を見る.
        monthly_sum_per_category = {}

        for category in unique_categories:
            category_data = self.all_data[self.all_data[self.categorycolumn] == category]
            monthly_sum = category_data.groupby(category_data[self.date_colum].dt.to_period('M'))[self.valuecolumn].sum()
            monthly_sum_per_category[category] = monthly_sum
        
        # カテゴリ毎の月単位合計利用金額を見る
        pie_data = {}
        total = 0

        for category, data in monthly_sum_per_category.items():
            if selected_month in data.index:
                pie_data[category] = data[selected_month]
                total += data[selected_month]
        
        # 各カテゴリの割合を計算
        pie_data_percentages = {k: v / total * 100 for k, v in pie_data.items()}

        # 円グラフの色を定義
        colors = plt.cm.Paired(range(len(pie_data)))

        # 円グラフの描画
        plt.pie(pie_data_percentages.values(), labels=pie_data_percentages.keys(), autopct='%1.1f%%', colors=colors)
        plt.title(f"{selected_month}のカテゴリ別利用額割合", fontproperties=self.font_prop)

        # 凡例の作成
        plt.legend(pie_data_percentages.keys(), loc="best", bbox_to_anchor=(1, 0, 0.5, 1), prop=self.font_prop, markerscale=0.5)

        plt.show()

    
    # 年毎のカード利用額推移をプロット. 円グラフも追加したいな.
    def plot_yearly_credit_usage(self):
        # まずself.all_datasから自動的にカテゴリを抽出.
        unique_categories = self.all_data[self.categorycolumn].unique()

        # 月毎にデータを集計
        monthly_data = self.all_data.groupby(self.all_data[self.date_colum].dt.to_period('M'))[self.valuecolumn].sum()
        # print(f"monthly_data = \n{monthly_data}") # ← Pandas Seriesというデータ型.

        # インデックスをdatetime型に戻す
        monthly_data.index = monthly_data.index.to_timestamp()
        #print(f"monthly_data = \n{monthly_data}") # ← Pandas Seriesというデータ型.

        # 単位をK単位に変換する.
        monthly_data_transformed = monthly_data.apply(lambda x: x / 1000)

        # 日付形式を変更する.今回は%mにする. 年は2023に固定されているので表示する必要はない.
        monthly_data_transformed.index = monthly_data_transformed.index.strftime('%m')
        #print(f"monthly_data_transformed = {monthly_data_transformed}")

        fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, figsize=(24, 6))
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
        pie_data = monthly_data_transformed.groupby(monthly_data_transformed.index).sum()
        colors = plt.cm.Paired(range(len(pie_data)))

        # 年間の月単位の支出円グラフの描画
        ax2.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', colors=colors)
        ax2.set_title('Percentage of Monthly Spending', fontproperties=self.font_prop)

        # カテゴリごとの年間支出を計算.
        category_spending = self.all_data.groupby(self.categorycolumn)[self.valuecolumn].sum()
        total_spending = category_spending.sum()
        category_spending_percentage = category_spending.apply(lambda x: (x / total_spending) * 100)

        # 5%未満のカテゴリを雑費に統合.
        misc_spending = category_spending_percentage[category_spending_percentage < 5].sum()
        category_spending_percentage = category_spending_percentage[category_spending_percentage >= 5]
        # print(f"category_spending_percentage = {category_spending_percentage}")
        category_spending_percentage['雑費'] = misc_spending
        print(f"category_spending_percentage['雑費'] = {category_spending_percentage['雑費']}")

        # カテゴリ毎の年間収支割合の円グラフの描画.
        ax3.pie(category_spending_percentage, labels=category_spending_percentage.index, autopct='%1.1f%%', colors=plt.cm.Paired(range(len(category_spending_percentage))))
        ax3.set_title('Annual Spending by Category', fontproperties=self.font_prop)


        # 各カテゴリの年間合計支出を計算
        category_total_spending = self.all_data.groupby(self.categorycolumn)[self.valuecolumn].sum()

        # 全体の合計支出を計算
        total_spending = category_total_spending.sum()

        # 各カテゴリの支出割合を計算
        category_spending_percentage = category_total_spending.apply(lambda x: x / total_spending * 100)

        # 5%未満のカテゴリを特定
        small_categories = category_spending_percentage[category_spending_percentage < 5].index

        # 5%未満のカテゴリに該当するデータを集計
        misc_categories_spending = self.all_data[self.all_data[self.categorycolumn].isin(small_categories)]
        misc_categories_total = misc_categories_spending.groupby(self.categorycolumn)[self.valuecolumn].sum()

        # 雑費の内訳の円グラフの描画
        ax4.pie(misc_categories_total, labels=misc_categories_total.index, autopct='%1.1f%%', colors=plt.cm.Paired(range(len(misc_categories_total))))
        ax4.set_title('Breakdown of Miscellaneous Spending', fontproperties=self.font_prop)

        # グラフの表示.
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    ca = Credit_Analysis()
    # メソッドの実行
    ca.plot_yearly_credit_usage()
    ca.get_category_and_plot_credit_spending()
    ca.plot_category_spending_pie()
