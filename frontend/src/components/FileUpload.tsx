import { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { motion, AnimatePresence } from "framer-motion";
import { X, Upload, FileText, FileType2, Presentation } from "lucide-react";
import { MAX_FILES, MAX_FILE_SIZE } from "@/lib/constants";
import { toast } from "react-hot-toast"; // Only import toast function

interface FileUploadProps {
    files: File[];
    setFiles: (files: File[]) => void;
}

const getFileIcon = (fileName: string) => {
    const extension = fileName.split('.').pop()?.toLowerCase();
    switch (extension) {
        case 'pdf':
            return <FileType2 className="text-red-500" />;
        case 'ppt':
        case 'pptx':
            return <Presentation className="text-orange-500" />;
        default:
            return <FileText className="text-blue-500" />;
    }
};

export default function FileUpload({ files, setFiles }: FileUploadProps) {
    const onDrop = useCallback((acceptedFiles: File[]) => {
        if (files.length >= MAX_FILES) {
            toast.error(`Maximum ${MAX_FILES} files allowed`);
            return;
        }

        // Filter out duplicates and files that exceed size limit
        const newFiles = acceptedFiles.filter(file => {
            if (file.size > MAX_FILE_SIZE) {
                toast.error(`File ${file.name} exceeds ${MAX_FILE_SIZE / 1024 / 1024}MB limit`, {
                    position: 'top-center'
                });
                return false;
            }
            if (files.some(existingFile => existingFile.name === file.name)) {
                toast.error(`File ${file.name} has already been added`);
                return false;
            }
            return true;
        });

        const updatedFiles = [...files, ...newFiles].slice(0, MAX_FILES);
        setFiles(updatedFiles);
    }, [files, setFiles]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'application/pdf': ['.pdf'],
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
            'text/plain': ['.txt']
        }
    });

    const removeFile = (name: string) => {
        setFiles(files.filter(file => file.name !== name));
    };

    return (
        <div className="w-full">
            <div
                {...getRootProps()}
                className={`
          glass-morphism rounded-xl p-12
          transition-all duration-300 cursor-pointer
          flex flex-col items-center justify-center
          min-h-[300px] relative overflow-hidden
          ${isDragActive ? 'dropzone-active' : 'hover:border-[#3A7DFF]'}
        `}
            >
                <input {...getInputProps()} />
                <motion.div
                    animate={{
                        scale: isDragActive ? 1.1 : 1,
                        opacity: isDragActive ? 0.8 : 1
                    }}
                    className="text-center"
                >
                    <Upload size={48} className="mx-auto mb-4 text-[#3A7DFF]" />
                    <p className="text-xl text-[#2C2C2C] font-medium mb-2">
                        {isDragActive
                            ? "Drop your files here..."
                            : "Drag and drop your files here"}
                    </p>
                    <p className="text-[#767676]">
                        or click to select files
                    </p>
                    <p className="text-sm text-[#767676] mt-4">
                        Supports PDF, PPT, DOC, TXT (max {MAX_FILE_SIZE / 1024 / 1024}MB per file)
                    </p>
                </motion.div>
                {files.length > 0 && (
                    <div className="absolute bottom-3 right-3 text-sm text-[#767676]">
                        {files.length}/{MAX_FILES}
                    </div>
                )}
            </div>

            <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 gap-4">
                <AnimatePresence>
                    {files.map(file => (
                        <motion.div
                            key={file.name}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            className="glass-morphism rounded-lg p-4 shadow-sm relative hover:scale-[1.02] transition-transform"
                        >
                            <button
                                onClick={() => removeFile(file.name)}
                                className="absolute top-2 right-2 p-1.5 rounded-full hover:bg-white/50 transition-colors"
                            >
                                <X size={16} className="text-[#316BDF]" />
                            </button>
                            <div className="flex items-center gap-3">
                                {getFileIcon(file.name)}
                                <p className="pr-8 truncate">{file.name}</p>
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>
            </div>
        </div>
    );
}