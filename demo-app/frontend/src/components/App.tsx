import { UnpackNestedValue, useForm } from "react-hook-form";
import {
  Button,
  Center,
  ChakraProvider,
  Grid,
  GridItem,
  Image, Flex, Box
} from "@chakra-ui/react";
import DragNDrop from "./fileUploader/FileUploader";
import React, { useState } from "react";
import FileUploaderContent from "./fileUploader/FileUploaderContent";
import ModelParameters from "./parameters/ModelParameters";
import { handleParametersSubmit } from "../service/service";
import { FormValues } from "../const/types";
import { saveAs } from "file-saver";

const App = () => {
  const [file, setFile] = useState<File>();
  const [imageUrl, setImageUrl] = useState('');
  const [xmlUrl, setXmlUrl] = useState('');
  const { register, handleSubmit } = useForm<FormValues>();

  const onSubmit = handleSubmit((data: UnpackNestedValue<FormValues>) => {
    if (file) {
      handleParametersSubmit({ data, file }).then((res: any) => {
        setImageUrl(res.data[0]);
        setXmlUrl(res.data[1]);
      });
    }
  });

  const imageDownload = () => {
    saveAs(imageUrl, 'image.png');
  }

  const xmlDownload = () => {
    saveAs(xmlUrl, 'model.xml');
  }

  const renderExportButton = () =>{
    if(xmlUrl){
      return <Button bg="#48BB78" size='md' m='5px 0' onClick={xmlDownload} >
              Download Model as BPMN 2.0 xml file
            </Button>
    } else {
      return <Box></Box>
    }
  }

  return (
    <ChakraProvider>

      <Flex justifyContent='space-between'>
        <Center h="100vh" bg="#F0FFF4" p='0 20px'>
        <form onSubmit={onSubmit}>
          <Grid
            h="50vh"
            w="50vw"
            templateColumns="repeat(2, 1fr)"
            templateRows="repeat(7, 1fr)"
            gap={6}
          >
            <GridItem colSpan={1} rowSpan={5}>
              <DragNDrop setFile={setFile}>
                <FileUploaderContent file={file} />
              </DragNDrop>
            </GridItem>

            <ModelParameters register={register} />

            <GridItem colSpan={2} rowSpan={2}>
              <Center h="100%">
                <Button
                  disabled={!file}
                  type="submit"
                  w="100%"
                  h="80%"
                  bg="#48BB78"
                >
                  Submit
                </Button>
              </Center>
            </GridItem>
          </Grid>
        </form>
        </Center>
        <Center h='100vh' w='100%' bg="#F0FFF4" p='0 20px'>
          <Flex direction='column'>
            <Image cursor='pointer'
                   maxH='90vh'
                   title='Click To Download image'
                   onClick={imageDownload}
                   border='3px solid black'
                   borderRadius='3px'
                   src={imageUrl}
                   alt="Discovered Model"
                   fallbackSrc='https://via.placeholder.com/150' />
            {renderExportButton()}
          </Flex>
        </Center>
        </Flex>
    </ChakraProvider>
  );
};

export default App;
