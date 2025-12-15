import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Progress } from "@/components/ui/progress";
import { Loader2, Upload, FileText, CheckCircle2, XCircle, AlertCircle } from "lucide-react";
import { toast } from "sonner";
import * as XLSX from "xlsx";

const ImportDialog = ({
  open,
  onOpenChange,
  title,
  description,
  entityType, // "lecturers", "subjects", "rooms", "programs", "canonical-groups"
  requiredColumns,
  optionalColumns = [], // Optional columns like "Description"
  onImport,
  sampleFileName,
}) => {
  const [file, setFile] = useState(null);
  const [previewData, setPreviewData] = useState([]);
  const [errors, setErrors] = useState([]);
  const [isValidating, setIsValidating] = useState(false);
  const [isImporting, setIsImporting] = useState(false);
  const [importProgress, setImportProgress] = useState(0);
  const [importResults, setImportResults] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileSelect = (event) => {
    const selectedFile = event.target.files[0];
    if (!selectedFile) return;

    // Validate file type
    const validExtensions = [".xlsx", ".xls", ".csv"];
    const fileExtension = selectedFile.name
      .substring(selectedFile.name.lastIndexOf("."))
      .toLowerCase();

    if (!validExtensions.includes(fileExtension)) {
      toast.error("Please select a valid Excel (.xlsx, .xls) or CSV (.csv) file");
      return;
    }

    // Validate file size (max 10MB)
    if (selectedFile.size > 10 * 1024 * 1024) {
      toast.error("File size must be less than 10MB");
      return;
    }

    setFile(selectedFile);
    setPreviewData([]);
    setErrors([]);
    setImportResults(null);
    parseFile(selectedFile);
  };

  const parseFile = async (fileToParse) => {
    setIsValidating(true);
    setErrors([]);

    try {
      const fileExtension = fileToParse.name
        .substring(fileToParse.name.lastIndexOf("."))
        .toLowerCase();

      let data = [];

      if (fileExtension === ".csv") {
        // Parse CSV
        const text = await fileToParse.text();
        const lines = text.split("\n").filter((line) => line.trim());
        if (lines.length === 0) {
          throw new Error("CSV file is empty");
        }

        const headers = lines[0].split(",").map((h) => h.trim().replace(/^"|"$/g, ""));
        for (let i = 1; i < lines.length; i++) {
          const values = lines[i].split(",").map((v) => v.trim().replace(/^"|"$/g, ""));
          if (values.some((v) => v)) {
            // Only add row if it has at least one non-empty value
            const row = {};
            headers.forEach((header, index) => {
              row[header] = values[index] || "";
            });
            data.push(row);
          }
        }
      } else {
        // Parse Excel
        const arrayBuffer = await fileToParse.arrayBuffer();
        const workbook = XLSX.read(arrayBuffer, { type: "array" });
        const firstSheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[firstSheetName];
        data = XLSX.utils.sheet_to_json(worksheet);
      }

      if (data.length === 0) {
        throw new Error("No data found in file");
      }

      // Validate columns
      const validationErrors = validateData(data, requiredColumns);
      setErrors(validationErrors);

      if (validationErrors.length === 0) {
        setPreviewData(data.slice(0, 10)); // Show first 10 rows as preview
        toast.success(`File parsed successfully. Found ${data.length} rows.`);
      } else {
        toast.error(`Validation failed. Please check the errors.`);
      }
    } catch (error) {
      toast.error(`Failed to parse file: ${error.message}`);
      setErrors([{ type: "parse", message: error.message }]);
    } finally {
      setIsValidating(false);
    }
  };

  // Normalize column names for matching (same logic as backend)
  const normalizeColumnName = (name) => {
    // Remove parentheses and their contents, then normalize (handles "Specializations(Subject Groups)" -> "specializations")
    const nameCleaned = name.replace(/\([^)]*\)/g, '').trim();
    // Normalize: lowercase, replace separators with spaces
    return nameCleaned.toLowerCase().replace(/[_\-\/]/g, ' ').replace(/\s+/g, ' ').trim();
  };

  const validateData = (data, requiredCols) => {
    const errors = [];

    if (data.length === 0) {
      errors.push({ type: "empty", message: "File contains no data rows" });
      return errors;
    }

    // Get headers from first row
    const headers = Object.keys(data[0]).map((h) => h.trim());
    
    // Normalize both required columns and headers for comparison
    const normalizedRequiredCols = requiredCols.map(col => normalizeColumnName(col));
    const normalizedHeaders = headers.map(h => normalizeColumnName(h));
    
    const missingColumns = requiredCols.filter((col, index) => {
      const normalizedCol = normalizedRequiredCols[index];
      return !normalizedHeaders.some(normalizedHeader => normalizedHeader === normalizedCol);
    });

    if (missingColumns.length > 0) {
      errors.push({
        type: "columns",
        message: `Missing required columns: ${missingColumns.join(", ")}`,
        missingColumns,
      });
    }

    // Validate each row
    data.forEach((row, index) => {
      requiredCols.forEach((col) => {
        const normalizedCol = normalizeColumnName(col);
        const header = headers.find((h) => normalizeColumnName(h) === normalizedCol);
        if (header && (!row[header] || row[header].toString().trim() === "")) {
          errors.push({
            type: "row",
            message: `Row ${index + 2}: Missing value for "${col}"`,
            row: index + 2,
            column: col,
          });
        }
      });
    });

    return errors;
  };

  const handleImport = async () => {
    if (errors.length > 0) {
      toast.error("Please fix validation errors before importing");
      return;
    }

    if (!file) {
      toast.error("Please select a file first");
      return;
    }

    setIsImporting(true);
    setImportProgress(0);
    setImportResults(null);

    try {
      // Parse full file again
      const fileExtension = file.name.substring(file.name.lastIndexOf(".")).toLowerCase();
      let fullData = [];

      if (fileExtension === ".csv") {
        const text = await file.text();
        const lines = text.split("\n").filter((line) => line.trim());
        const headers = lines[0].split(",").map((h) => h.trim().replace(/^"|"$/g, ""));
        for (let i = 1; i < lines.length; i++) {
          const values = lines[i].split(",").map((v) => v.trim().replace(/^"|"$/g, ""));
          if (values.some((v) => v)) {
            const row = {};
            headers.forEach((header, index) => {
              row[header] = values[index] || "";
            });
            fullData.push(row);
          }
        }
      } else {
        const arrayBuffer = await file.arrayBuffer();
        const workbook = XLSX.read(arrayBuffer, { type: "array" });
        const firstSheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[firstSheetName];
        fullData = XLSX.utils.sheet_to_json(worksheet);
      }

      setImportProgress(30);

      // Call the import function passed as prop
      const results = await onImport(fullData, (progress) => {
        setImportProgress(30 + (progress * 0.7)); // 30-100%
      });

      setImportProgress(100);
      setImportResults(results);

      if (results.success) {
        toast.success(
          `Successfully imported ${results.imported || 0} ${entityType}. ${results.errors?.length || 0} errors.`
        );
      } else {
        toast.error(`Import failed: ${results.error || "Unknown error"}`);
      }
    } catch (error) {
      toast.error(`Import failed: ${error.message}`);
      setImportResults({ success: false, error: error.message });
    } finally {
      setIsImporting(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setPreviewData([]);
    setErrors([]);
    setImportResults(null);
    setImportProgress(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleClose = () => {
    if (!isImporting) {
      handleReset();
      onOpenChange(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{title || `Import ${entityType}`}</DialogTitle>
          <DialogDescription>
            {description || `Upload an Excel (.xlsx, .xls) or CSV (.csv) file to import ${entityType}.`}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* File Upload */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Select File</label>
            <div className="flex items-center gap-4">
              <input
                ref={fileInputRef}
                type="file"
                accept=".xlsx,.xls,.csv"
                onChange={handleFileSelect}
                className="hidden"
                id="file-upload"
                disabled={isImporting || isValidating}
              />
              <label
                htmlFor="file-upload"
                className="flex items-center gap-2 px-4 py-2 border border-dashed rounded-lg cursor-pointer hover:bg-accent transition-colors"
              >
                <Upload className="h-4 w-4" />
                <span>{file ? file.name : "Choose file..."}</span>
              </label>
              {file && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleReset}
                  disabled={isImporting || isValidating}
                >
                  Clear
                </Button>
              )}
            </div>
            {sampleFileName && (
              <p className="text-xs text-muted-foreground">
                Download sample template:{" "}
                <a
                  href={`/templates/${sampleFileName}`}
                  download
                  className="text-primary hover:underline"
                >
                  {sampleFileName}
                </a>
              </p>
            )}
          </div>

          {/* Required Columns Info */}
          <div className="bg-muted/50 p-3 rounded-lg space-y-3">
            <div>
              <p className="text-sm font-medium mb-2">Required Columns:</p>
              <div className="flex flex-wrap gap-2">
                {requiredColumns.map((col) => (
                  <span
                    key={col}
                    className="px-2 py-1 bg-background rounded text-xs font-mono"
                  >
                    {col}
                  </span>
                ))}
              </div>
            </div>
            {optionalColumns.length > 0 && (
              <div>
                <p className="text-sm font-medium mb-2">Optional Columns:</p>
                <div className="flex flex-wrap gap-2">
                  {optionalColumns.map((col) => (
                    <span
                      key={col}
                      className="px-2 py-1 bg-background/50 rounded text-xs font-mono text-muted-foreground"
                    >
                      {col}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Validation Status */}
          {isValidating && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              Validating file...
            </div>
          )}

          {/* Errors */}
          {errors.length > 0 && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                <div className="space-y-1">
                  <p className="font-medium">Validation Errors:</p>
                  <ul className="list-disc list-inside text-sm space-y-1">
                    {errors.slice(0, 10).map((error, index) => (
                      <li key={index}>{error.message}</li>
                    ))}
                    {errors.length > 10 && (
                      <li className="text-muted-foreground">
                        ...and {errors.length - 10} more errors
                      </li>
                    )}
                  </ul>
                </div>
              </AlertDescription>
            </Alert>
          )}

          {/* Preview Data */}
          {previewData.length > 0 && errors.length === 0 && (
            <div className="space-y-2">
              <p className="text-sm font-medium">
                Preview (showing first {previewData.length} rows):
              </p>
              <div className="border rounded-lg overflow-x-auto max-h-64">
                <table className="w-full text-xs">
                  <thead className="bg-muted">
                    <tr>
                      {Object.keys(previewData[0]).map((header) => (
                        <th key={header} className="px-2 py-1 text-left font-medium">
                          {header}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {previewData.map((row, index) => (
                      <tr key={index} className="border-t">
                        {Object.keys(previewData[0]).map((header) => (
                          <td key={header} className="px-2 py-1">
                            {row[header] || "-"}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Import Progress */}
          {isImporting && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span>Importing...</span>
                <span>{Math.round(importProgress)}%</span>
              </div>
              <Progress value={importProgress} />
            </div>
          )}

          {/* Import Results */}
          {importResults && (
            <Alert variant={importResults.success ? "default" : "destructive"}>
              {importResults.success ? (
                <CheckCircle2 className="h-4 w-4" />
              ) : (
                <XCircle className="h-4 w-4" />
              )}
              <AlertDescription>
                {importResults.success ? (
                  <div>
                    <p className="font-medium">Import Completed Successfully!</p>
                    <p className="text-sm mt-1">
                      Imported: {importResults.imported || 0} | Errors:{" "}
                      {importResults.errors?.length || 0}
                    </p>
                    {importResults.errors && importResults.errors.length > 0 && (
                      <ul className="list-disc list-inside text-sm mt-2">
                        {importResults.errors.slice(0, 5).map((err, idx) => (
                          <li key={idx}>{err}</li>
                        ))}
                        {importResults.errors.length > 5 && (
                          <li>...and {importResults.errors.length - 5} more errors</li>
                        )}
                      </ul>
                    )}
                  </div>
                ) : (
                  <p>{importResults.error || "Import failed"}</p>
                )}
              </AlertDescription>
            </Alert>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleClose} disabled={isImporting}>
            {importResults ? "Close" : "Cancel"}
          </Button>
          {!importResults && (
            <Button
              onClick={handleImport}
              disabled={!file || errors.length > 0 || isValidating || isImporting}
            >
              {isImporting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Importing...
                </>
              ) : (
                <>
                  <FileText className="h-4 w-4 mr-2" />
                  Import
                </>
              )}
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default ImportDialog;

