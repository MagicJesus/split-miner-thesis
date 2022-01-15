import { Center, Grid, GridItem, Heading } from "@chakra-ui/react";
import { AttachmentIcon } from "@chakra-ui/icons";
import React from "react";

const FileUploaderContent = ({ file }: { file?: File }) => (
  <Grid templateRows="repeat(4, 1fr)" w="100%">
    <GridItem rowSpan={3}>
      <Center>
        <AttachmentIcon w="30%" h="30%" />
      </Center>
    </GridItem>
    <Center>
      <Heading as="h5" size="sm">
        {file ? `File name: ${file.name}` : "No files uploaded yet"}
      </Heading>
    </Center>
  </Grid>
);

export default FileUploaderContent;
