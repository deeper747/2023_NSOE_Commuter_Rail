Sub Extract_P7_RLR()
'
' Extract_RLR Macro
'

'
    Dim url_rng As Range
    Dim monyr_rng As Range
    Dim i As Integer
    
    End_UP = Worksheets("URL").Range("H1").End(xlDown).Address
    End_SN = Worksheets("URL").Range("I1").End(xlDown).Address
    Set url_rng = Range("H1", End_UP)
    Set monyr_rng = Range("I1", End_SN)
    'ActiveWorkbook.Queries("Page007").Delete
    
    For i = 1 To url_rng.Cells.Count
        Dim filePath As String
        filePath = url_rng.Cells(i).Text
        
        ActiveWorkbook.Queries.Add Name:="Page007", Formula:= _
            "let" & Chr(13) & "" & Chr(10) & "    Source = Pdf.Tables(File.Contents(""" & filePath & """), [Implementation=""1.3""])," & Chr(13) & "" & Chr(10) & "    Page1 = Source{[Id=""Page007""]}[Data]," & Chr(13) & "" & Chr(10) & "    #""Changed Type"" = Table.TransformColumnTypes(Page1,{{""Column1"", type text}, {""Colu" & _
            "mn2"", type text}, {""Column3"", type text}, {""Column4"", type text}, {""Column5"", type text}, {""Column6"", type text}, {""Column7"", type text}, {""Column8"", type text}, {""Column9"", type text}, {""Column10"", type text}, {""Column11"", type text}, {""Column12"", type text}, {""Column13"", type text}, {""Column14"", type text}, {""Column15"", type text}, {""Co" & _
            "lumn16"", type text}})" & Chr(13) & "" & Chr(10) & "in" & Chr(13) & "" & Chr(10) & "    #""Changed Type"""
        ActiveWorkbook.Worksheets.Add
        With ActiveSheet.ListObjects.Add(SourceType:=0, Source:= _
            "OLEDB;Provider=Microsoft.Mashup.OleDb.1;Data Source=$Workbook$;Location=Page007;Extended Properties=""""" _
            , Destination:=Range("$A$1")).QueryTable
            .CommandType = xlCmdSql
            .CommandText = Array("SELECT * FROM [Page007]")
            .RowNumbers = False
            .FillAdjacentFormulas = False
            .PreserveFormatting = True
            .RefreshOnFileOpen = False
            .BackgroundQuery = True
            .RefreshStyle = xlInsertDeleteCells
            .SavePassword = False
            .SaveData = True
            .AdjustColumnWidth = True
            .RefreshPeriod = 0
            .PreserveColumnInfo = True
            .Refresh BackgroundQuery:=False
        End With
        Cells.Select
        Selection.Copy
        Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, SkipBlanks _
        :=False, Transpose:=False
        ActiveSheet.Name = monyr_rng.Cells(i)
        ActiveWorkbook.Queries("Page007").Delete
        Sheets("URL").Select
    Next
End Sub

Sub Extract_P7_RLR_2()
'
' Extract_RLR_2 Macro
'

'
    Dim url_rng As Range
    Dim monyr_rng As Range
    Dim i As Integer
    
    End_UP = Worksheets("URL_2").Range("H1").End(xlDown).Address
    End_SN = Worksheets("URL_2").Range("I1").End(xlDown).Address
    Set url_rng = Worksheets("URL_2").Range("H1", End_UP)
    Set monyr_rng = Worksheets("URL_2").Range("I1", End_SN)
    ActiveWorkbook.Queries("Page007").Delete
    
    For i = 1 To url_rng.Cells.Count
        Dim filePath As String
        filePath = url_rng.Cells(i).Text
        
        ActiveWorkbook.Queries.Add Name:="Page007", Formula:= _
            "let" & Chr(13) & "" & Chr(10) & "    Source = Pdf.Tables(File.Contents(""" & filePath & """), [Implementation=""1.3""])," & Chr(13) & "" & Chr(10) & "    Page1 = Source{[Id=""Page007""]}[Data]," & Chr(13) & "" & Chr(10) & "    #""Changed Type"" = Table.TransformColumnTypes(Page1,{{""Column1"", type text}, {""Column2" & _
            """, type text}, {""Column3"", type text}, {""Column4"", type text}, {""Column5"", type text}, {""Column6"", type text}, {""Column7"", type text}, {""Column8"", type text}, {""Column9"", type text}, {""Column10"", type text}, {""Column11"", type text}, {""Column12"", type text}, {""Column13"", type text}})" & Chr(13) & "" & Chr(10) & "in" & Chr(13) & "" & Chr(10) & "    #""Changed Type"""
        ActiveWorkbook.Worksheets.Add
        With ActiveSheet.ListObjects.Add(SourceType:=0, Source:= _
            "OLEDB;Provider=Microsoft.Mashup.OleDb.1;Data Source=$Workbook$;Location=""Page007"";Extended Properties=""""" _
            , Destination:=Range("$A$1")).QueryTable
            .CommandType = xlCmdSql
            .CommandText = Array("SELECT * FROM [Page007]")
            .RowNumbers = False
            .FillAdjacentFormulas = False
            .PreserveFormatting = True
            .RefreshOnFileOpen = False
            .BackgroundQuery = True
            .RefreshStyle = xlInsertDeleteCells
            .SavePassword = False
            .SaveData = True
            .AdjustColumnWidth = True
            .RefreshPeriod = 0
            .PreserveColumnInfo = True
            .Refresh BackgroundQuery:=False
        End With
        Cells.Select
        Selection.Copy
        Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, SkipBlanks _
        :=False, Transpose:=False
        ActiveSheet.Name = monyr_rng.Cells(i)
        ActiveWorkbook.Queries("Page007").Delete
    Next
End Sub

Sub Extract_P7_RLR_3()
'
' Extract_RLR_3 Macro
'

'
    Dim url_rng As Range
    Dim monyr_rng As Range
    Dim i As Integer
    
    End_UP = Worksheets("URL_3").Range("H1").End(xlDown).Address
    End_SN = Worksheets("URL_3").Range("I1").End(xlDown).Address
    Set url_rng = Worksheets("URL_3").Range("H1", End_UP)
    Set monyr_rng = Worksheets("URL_3").Range("I1", End_SN)
    'ActiveWorkbook.Queries("Page007").Delete
    
    For i = 1 To url_rng.Cells.Count
        Dim filePath As String
        filePath = url_rng.Cells(i).Text
        
        ActiveWorkbook.Queries.Add Name:="Page007", Formula:= _
            "let" & Chr(13) & "" & Chr(10) & "    Source = Pdf.Tables(File.Contents(""" & filePath & """), [Implementation=""1.3""])," & Chr(13) & "" & Chr(10) & "    Page1 = Source{[Id=""Page007""]}[Data]," & Chr(13) & "" & Chr(10) & "    #""Changed Type"" = Table.TransformColumnTypes(Page1,{{""Column1"", type text}, {""Colu" & _
            "mn2"", type text}, {""Column3"", type text}, {""Column4"", type text}, {""Column5"", type text}, {""Column6"", type text}, {""Column7"", type text}, {""Column8"", type text}, {""Column9"", type number}, {""Column10"", type text}, {""Column11"", type text}, {""Column12"", type text}, {""Column13"", type text}, {""Column14"", type text}, {""Column15"", type text}, {""" & _
            "Column16"", type text}, {""Column17"", Int64.Type}})" & Chr(13) & "" & Chr(10) & "in" & Chr(13) & "" & Chr(10) & "    #""Changed Type"""
        ActiveWorkbook.Worksheets.Add
        With ActiveSheet.ListObjects.Add(SourceType:=0, Source:= _
            "OLEDB;Provider=Microsoft.Mashup.OleDb.1;Data Source=$Workbook$;Location=""Page007"";Extended Properties=""""" _
            , Destination:=Range("$A$1")).QueryTable
            .CommandType = xlCmdSql
            .CommandText = Array("SELECT * FROM [Page007]")
            .RowNumbers = False
            .FillAdjacentFormulas = False
            .PreserveFormatting = True
            .RefreshOnFileOpen = False
            .BackgroundQuery = True
            .RefreshStyle = xlInsertDeleteCells
            .SavePassword = False
            .SaveData = True
            .AdjustColumnWidth = True
            .RefreshPeriod = 0
            .PreserveColumnInfo = True
            .Refresh BackgroundQuery:=False
        End With
        Cells.Select
        Selection.Copy
        Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, SkipBlanks _
        :=False, Transpose:=False
        ActiveSheet.Name = monyr_rng.Cells(i)
        ActiveWorkbook.Queries("Page007").Delete
    Next
End Sub

Sub Extract_P7_RLR_4()
'
' Extract_RLR_4 Macro
'

'
    Dim url_rng As Range
    Dim monyr_rng As Range
    Dim i As Integer
    
    End_UP = Worksheets("URL_4").Range("H1").End(xlDown).Address
    End_SN = Worksheets("URL_4").Range("I1").End(xlDown).Address
    Set url_rng = Worksheets("URL_4").Range("H1", End_UP)
    Set monyr_rng = Worksheets("URL_4").Range("I1", End_SN)
    'ActiveWorkbook.Queries("Page007").Delete
    
    For i = 1 To url_rng.Cells.Count
        Dim filePath As String
        filePath = url_rng.Cells(i).Text
        
        ActiveWorkbook.Queries.Add Name:="Page007", Formula:= _
            "let" & Chr(13) & "" & Chr(10) & "    Source = Pdf.Tables(File.Contents(""" & filePath & """), [Implementation=""1.3""])," & Chr(13) & "" & Chr(10) & "    Page1 = Source{[Id=""Page007""]}[Data]," & Chr(13) & "" & Chr(10) & "    #""Changed Type"" = Table.TransformColumnTypes(Page1,{{""Column1"", type text}, {""Column" & _
            "2"", type text}, {""Column3"", type text}, {""Column4"", type text}, {""Column5"", type text}, {""Column6"", type text}, {""Column7"", type text}, {""Column8"", type number}, {""Column9"", type text}, {""Column10"", type text}, {""Column11"", type text}, {""Column12"", type text}, {""Column13"", type text}, {""Column14"", Int64.Type}})" & Chr(13) & "" & Chr(10) & "in" & Chr(13) & "" & Chr(10) & "    #""Changed Type"""
        ActiveWorkbook.Worksheets.Add
        With ActiveSheet.ListObjects.Add(SourceType:=0, Source:= _
            "OLEDB;Provider=Microsoft.Mashup.OleDb.1;Data Source=$Workbook$;Location=""Page007"";Extended Properties=""""" _
            , Destination:=Range("$A$1")).QueryTable
            .CommandType = xlCmdSql
            .CommandText = Array("SELECT * FROM [Page007]")
            .RowNumbers = False
            .FillAdjacentFormulas = False
            .PreserveFormatting = True
            .RefreshOnFileOpen = False
            .BackgroundQuery = True
            .RefreshStyle = xlInsertDeleteCells
            .SavePassword = False
            .SaveData = True
            .AdjustColumnWidth = True
            .RefreshPeriod = 0
            .PreserveColumnInfo = True
            .Refresh BackgroundQuery:=False
        End With
        Cells.Select
        Selection.Copy
        Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, SkipBlanks _
        :=False, Transpose:=False
        ActiveSheet.Name = monyr_rng.Cells(i)
        ActiveWorkbook.Queries("Page007").Delete
    Next
End Sub

Sub Extract_P7_RLR_5()
'
' Extract_RLR_5 Macro
'

'
    Dim url_rng As Range
    Dim monyr_rng As Range
    Dim i As Integer
    
    End_UP = Worksheets("URL_5").Range("H1").End(xlDown).Address
    End_SN = Worksheets("URL_5").Range("I1").End(xlDown).Address
    Set url_rng = Worksheets("URL_5").Range("H1", End_UP)
    Set monyr_rng = Worksheets("URL_5").Range("I1", End_SN)
    ActiveWorkbook.Queries("Page007").Delete
    
    For i = 5 To url_rng.Cells.Count
        Dim filePath As String
        filePath = url_rng.Cells(i).Text
        
        ActiveWorkbook.Queries.Add Name:="Page007", Formula:= _
            "let" & Chr(13) & "" & Chr(10) & "    Source = Pdf.Tables(File.Contents(""" & filePath & """), [Implementation=""1.3""])," & Chr(13) & "" & Chr(10) & "    Page1 = Source{[Id=""Page007""]}[Data]," & Chr(13) & "" & Chr(10) & "   #""Changed Type"" = Table.TransformColumnTypes(Page1,{{""Column1"", type text}, {""Column" & _
            "2"", type text}, {""Column3"", type text}, {""Column4"", type text}, {""Column5"", type text}, {""Column6"", type text}, {""Column7"", type text}, {""Column8"", type text}, {""Column9"", type text}, {""Column10"", type text}, {""Column11"", ty" & _
            "pe text}, {""Column12"", type text}, {""Column13"", type text}, {""Column14"", type text}, {""Column15"", Int64.Type}})" & Chr(13) & "" & Chr(10) & "in" & Chr(13) & "" & Chr(10) & "    #""Changed Type"""
        ActiveWorkbook.Worksheets.Add
        With ActiveSheet.ListObjects.Add(SourceType:=0, Source:= _
            "OLEDB;Provider=Microsoft.Mashup.OleDb.1;Data Source=$Workbook$;Location=Page007;Extended Properties=""""" _
            , Destination:=Range("$A$1")).QueryTable
            .CommandType = xlCmdSql
            .CommandText = Array("SELECT * FROM [Page007]")
            .RowNumbers = False
            .FillAdjacentFormulas = False
            .PreserveFormatting = True
            .RefreshOnFileOpen = False
            .BackgroundQuery = True
            .RefreshStyle = xlInsertDeleteCells
            .SavePassword = False
            .SaveData = True
            .AdjustColumnWidth = True
            .RefreshPeriod = 0
            .PreserveColumnInfo = True
            .Refresh BackgroundQuery:=False
        End With
        
        Cells.Select
        Selection.Copy
        Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, SkipBlanks _
        :=False, Transpose:=False
        ActiveSheet.Name = monyr_rng.Cells(i)
        ActiveWorkbook.Queries("Page007").Delete
    Next
End Sub

Sub Extract_P7_RLR_6()
'
' Extract_RLR_6 Macro
'

'
    Dim url_rng As Range
    Dim monyr_rng As Range
    Dim i As Integer
    
    End_UP = Worksheets("URL_6").Range("H1").End(xlDown).Address
    End_SN = Worksheets("URL_6").Range("I1").End(xlDown).Address
    Set url_rng = Worksheets("URL_6").Range("H1", End_UP)
    Set monyr_rng = Worksheets("URL_6").Range("I1", End_SN)
    ActiveWorkbook.Queries("Page007").Delete
    
    For i = 14 To url_rng.Cells.Count
        Dim filePath As String
        filePath = url_rng.Cells(i).Text
        
        ActiveWorkbook.Queries.Add Name:="Page007", Formula:= _
            "let" & Chr(13) & "" & Chr(10) & "    Source = Pdf.Tables(File.Contents(""" & filePath & """), [Implementation=""1.3""])," & Chr(13) & "" & Chr(10) & "    Page1 = Source{[Id=""Page007""]}[Data]," & Chr(13) & "" & Chr(10) & "    #""Changed Type"" = Table.TransformColumnTypes(Page1,{{""Column1"", type text}, {""Column" & _
            "2"", type text}, {""Column3"", type text}, {""Column4"", type text}, {""Column5"", type text}, {""Column6"", type text}, {""Column7"", type text}, {""Column8"", type text}, {""Column9"", type text}, {""Column10"", type text}, {""Column11"", ty" & _
            "pe text}, {""Column12"", type text}, {""Column13"", type text}, {""Column14"", type text}, {""Column15"", type text}, {""Column16"", type text}, {""Column17"", type text}, {""Column18"", type text}, {""Column19"", type text}, {""Column20"", type text}})" & Chr(13) & "" & Chr(10) & "in" & Chr(13) & "" & Chr(10) & "    #""Changed Type"""
        ActiveWorkbook.Worksheets.Add
        With ActiveSheet.ListObjects.Add(SourceType:=0, Source:= _
            "OLEDB;Provider=Microsoft.Mashup.OleDb.1;Data Source=$Workbook$;Location=Page007;Extended Properties=""""" _
            , Destination:=Range("$A$1")).QueryTable
            .CommandType = xlCmdSql
            .CommandText = Array("SELECT * FROM [Page007]")
            .RowNumbers = False
            .FillAdjacentFormulas = False
            .PreserveFormatting = True
            .RefreshOnFileOpen = False
            .BackgroundQuery = True
            .RefreshStyle = xlInsertDeleteCells
            .SavePassword = False
            .SaveData = True
            .AdjustColumnWidth = True
            .RefreshPeriod = 0
            .PreserveColumnInfo = True
            .Refresh BackgroundQuery:=False
        End With
        
        Cells.Select
        Selection.Copy
        Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, SkipBlanks _
        :=False, Transpose:=False
        ActiveSheet.Name = monyr_rng.Cells(i)
        ActiveWorkbook.Queries("Page007").Delete
    Next
End Sub

