# Python-Scrawer-591rent

### 1.由原本變數刪減至13個變數。
變數：id 標題 行政區 地址 總價 單價 總坪數 主建物坪數 房數 樓層 屋齡 使用分區 建物型態
### 2.地址轉換出經緯度。
### 3.房數切割成房廳衛3個變數欄位 並且刪除0衛的資料。
### 4.樓層切割為總樓層與移轉樓層 並且刪除透天 與 1樓資料。
### 5.ID刪除重複資料。
### 6.標題刪除有含車位的關鍵字。
### 7.建物型態刪除透天。
### 8.除了id相同 由於591的資料有很多仲介或屋主刊登。
### 9.因此透過程式比對變數藉此刪除重複資料，如相同總價 坪數 移轉樓層 總樓層 屋齡 地址 則視為相同資料。
