def start_camera(self):
        """Starts the camera for barcode scanning."""
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            # Scan the frame for barcodes
            barcodes = decode(frame)
            for barcode in barcodes:
                barcode_data = barcode.data.decode('utf-8')
                logger.info(f"Barcode detected: {barcode_data}")
                self.get_nutritional_info(barcode_data)

                pts = barcode.polygon
                if len(pts) == 4:
                    cv2.polylines(frame, [np.array(pts, np.int32)], True, (0, 255, 0), 3)
            
            cv2.imshow('Barcode Scanner', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

    def scan_food(self, image_path):
        """Scans a food item by its barcode image and logs nutritional info.

        Args:
            image_path (str): Path to the barcode image file.
        """
        barcode = self.decode_barcode(image_path)
        if barcode:
            nutritional_info = self.get_nutritional_info(barcode)
            self.log_food(nutritional_info)
    
    # get nutritional information off of food database 
    def get_nutritional_info(self, barcode):
        """Fetches nutritional information for the scanned barcode.

        Args:
            barcode (str): The barcode of the food item.

        Returns:
            dict: Nutritional information of the product if found, else None.
        """
        try:
            api_url = f'https://world.openfoodfacts.org/api/v0/product/{barcode}.json'
            response = requests.get(api_url)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            product_data = response.json()
            if product_data['status'] == 1:  
                return product_data['product']
            else:
                logger.warning("Product not found")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f'API request failed: {e}')
            return None
