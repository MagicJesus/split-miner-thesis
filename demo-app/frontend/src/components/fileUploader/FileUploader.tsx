import React from "react";
import { FileUploader } from "react-drag-drop-files";
import "../../styles/App.css";

interface DragNDropProps {
  setFile?: React.Dispatch<React.SetStateAction<File | undefined>>;
}

const DragNDrop = ({
  setFile,
  children,
}: React.PropsWithChildren<DragNDropProps>) => {
  const handleChange = (file: File) => {
    if (setFile) {
      setFile(file);
    }
  };
  return (
    <FileUploader
      style={{ height: "100%", color: "red" }}
      maxSize={50}
      handleChange={handleChange}
      name="file"
    >
      {children}
    </FileUploader>
  );
};

export default DragNDrop;
