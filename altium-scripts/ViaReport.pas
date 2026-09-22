{ ViaReport.pas - Altium DelphiScript
  Lists every via on the current PCB (net, drill, diameter, layer span) to a CSV next to the PcbDoc,
  and shows a summary of how many vias use each drill size.

  Why: fewer distinct drill sizes = lower fab cost (Chapter 24); unexpected via spans reveal
  routing mistakes; the via count per net helps review high-speed nets (Chapter 17).

  Run: open a PcbDoc, then File > Run Script... > select ViaReport.pas > RunViaReport
  (Add the .pas to a Script Project (.PrjScr) first if Altium asks for one.) }

Procedure RunViaReport;
Var
    Board     : IPCB_Board;
    Iterator  : IPCB_BoardIterator;
    Via       : IPCB_Via;
    Csv       : TStringList;
    Summary   : TStringList;
    NetName   : String;
    Key       : String;
    I, Total  : Integer;
    OutPath   : String;
    Msg       : String;
Begin
    Board := PCBServer.GetCurrentPCBBoard;
    If Board = Nil Then
    Begin
        ShowMessage('Open a PCB document first.');
        Exit;
    End;

    Csv := TStringList.Create;
    Summary := TStringList.Create;
    Csv.Add('Net,X_mm,Y_mm,Drill_mm,Diameter_mm,FromLayer,ToLayer');
    Total := 0;

    Iterator := Board.BoardIterator_Create;
    Iterator.AddFilter_ObjectSet(MkSet(eViaObject));
    Iterator.AddFilter_LayerSet(AllLayers);
    Iterator.AddFilter_Method(eProcessAll);

    Via := Iterator.FirstPCBObject;
    While Via <> Nil Do
    Begin
        If Via.Net <> Nil Then NetName := Via.Net.Name Else NetName := '(no net)';

        Csv.Add(NetName + ',' +
                FormatFloat('0.000', CoordToMMs(Via.x - Board.XOrigin)) + ',' +
                FormatFloat('0.000', CoordToMMs(Via.y - Board.YOrigin)) + ',' +
                FormatFloat('0.000', CoordToMMs(Via.HoleSize)) + ',' +
                FormatFloat('0.000', CoordToMMs(Via.Size)) + ',' +
                Layer2String(Via.LowLayer) + ',' + Layer2String(Via.HighLayer));

        { summary keyed by drill / diameter }
        Key := FormatFloat('0.000', CoordToMMs(Via.HoleSize)) + ' / ' + FormatFloat('0.000', CoordToMMs(Via.Size)) + ' mm';
        I := Summary.IndexOfName(Key);
        If I < 0 Then
            Summary.Add(Key + '=1')
        Else
            Summary.Values[Key] := IntToStr(StrToInt(Summary.Values[Key]) + 1);

        Inc(Total);
        Via := Iterator.NextPCBObject;
    End;
    Board.BoardIterator_Destroy(Iterator);

    OutPath := ChangeFileExt(Board.FileName, '') + '_vias.csv';
    Csv.SaveToFile(OutPath);

    Msg := 'Total vias: ' + IntToStr(Total) + #13#10 + 'Drill / diameter : count' + #13#10;
    For I := 0 To Summary.Count - 1 Do
        Msg := Msg + '  ' + Summary.Names[I] + ' : ' + Summary.ValueFromIndex[I] + #13#10;
    Msg := Msg + #13#10 + 'CSV written to: ' + OutPath;
    ShowMessage(Msg);

    Csv.Free;
    Summary.Free;
End;
