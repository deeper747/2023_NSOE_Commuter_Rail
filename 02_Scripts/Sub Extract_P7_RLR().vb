Sub Extract_P7_RLR()
'
' Extract_RLR Macro
'

'
    Dim url_rng As Range
    Dim monyr_rng As Range
    Dim query_name As Range
    Dim i As Integer
    
'    End_UP = Range("H1").End(xlDown).Cells
'    End_SN = Range("I1").End(xlDown).Cells
    
    Set url_rng = Range("H1:H72")
    Set monyr_rng = Range("I1:I72")
    Set query_name = Range("J1:J72")
    For i = 1 To url_rng.Cells.Count
        Dim currentQueryName As String
        currentQueryName = query_name.Cells(i).Text
        ActiveWorkbook.Queries.Add Name:=currentQueryName, Formula:= _
            "let" & Chr(13) & "" & Chr(10) & "    Source = Pdf.Tables(File.Contents(""url_range.Cells(i)""), [Implementation=""1.3""])," & Chr(13) & "" & Chr(10) & "    Page1 = Source{[Id=""Page007""]}[Data]," & Chr(13) & "" & Chr(10) & "    #""Changed Type"" = Table.TransformColumnTypes(Page1,{{""Column1"", type text}, {""Colu" & _
            "mn2"", type text}, {""Column3"", type text}, {""Column4"", type text}, {""Column5"", type text}, {""Column6"", type text}, {""Column7"", type text}, {""Column8"", type text}, {""Column9"", type text}, {""Column10"", type text}, {""Column11"", type text}, {""Column12"", type text}, {""Column13"", type text}, {""Column14"", type text}, {""Column15"", type text}, {""Co" & _
            "lumn16"", type text}})" & Chr(13) & "" & Chr(10) & "in" & Chr(13) & "" & Chr(10) & "    #""Changed Type"""
        Dim newSheet As Worksheet
        Set newSheet = ActiveWorkbook.Worksheets.Add
        With ActiveSheet.ListObjects.Add(SourceType:=0, Source:= _
            "OLEDB;Provider=Microsoft.Mashup.OleDb.1;Data Source=$Workbook$;Location=Page007;Extended Properties=""""" _
            , Destination:=Range("$A$1")).QueryTable
            .CommandType = xlCmdSql
            .CommandText = Array("SELECT * FROM [currentQueryName]")
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
            .ListObject.DisplayName = currentQueryName
            .Refresh BackgroundQuery:=False
        End With
        newSheet.Name = monyr_rng.Cells(i).Text
        Sheets("URL").Select
    Next
End Sub


