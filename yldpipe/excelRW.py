
class ExcelRW:

  def csv2xlsx(self):
    """ create excel file from multiple csv files """
    c = 0
    read_file= {}
    # needed?
    # self.load_fieldnames()

    for out_fn in out_fns:
      out_fnp = str(data_out.joinpath('SI/csv_pd/'+out_fn))
      #out_fnp = str(data_in.joinpath('SI/csv_pd/'+out_fn))
      sheet_name = out_fn[:-4]
      read_file[c] = pd.read_csv(out_fnp)
      logger.debug("row count of sheet %s is %s", sheet_name, len(read_file[c]))
      c += 1

    c = 0
    with pd.ExcelWriter(dstfn, engine='xlsxwriter') as writer:
      for out_fn in out_fns:
        logger.info("write excel sheet %s", sheet_name)
        sheet_name = out_fn[:-4]
        read_file[c].to_excel(writer, sheet_name=sheet_name, index=False)
        #logger.debug("wrote fields to %s : %s", sheet_name, self.fnames[c])
        for column in read_file[c]:
          column_length = max(read_file[c][column].astype(str).map(len).max(), len(column))
          logger.debug("max is %s", column_length)
          col_idx = read_file[c].columns.get_loc(column)
          writer.sheets[sheet_name].set_column(col_idx, col_idx, column_length)
        c += 1
        
  def background_colors(path):
      workbook = Workbook()
      sheet = workbook.active
      yellow = "00FFFF00"
      for rows in sheet.iter_rows(min_row=1, max_row=10, min_col=1, max_col=12):
          for cell in rows:
              if cell.row % 2:
                  cell.fill = PatternFill(start_color=yellow, end_color=yellow,
                                          fill_type = "solid")
      workbook.save(path)



