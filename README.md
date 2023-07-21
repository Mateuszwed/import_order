# import_order

<h3>PL</h3>

Moduł Import Order to narzędzie do importu danych dla systemu Odoo. Został stworzony z myślą o zapewnieniu łatwej i wydajnej metody importowania zamówień z plików CSV.

Jedną z najważniejszych funkcji modułu jest możliwość tworzenia nowych klientów, firm, adresów dostawy i faktury podczas procesu importu. Moduł sprawdza, czy dany klient, firma lub adres już istnieje w systemie. Jeżeli nie, moduł automatycznie tworzy nowy rekord z danymi z pliku CSV.

Dodatkowo, moduł zawiera funkcjonalność do wyszukiwania produktów na podstawie nazwy, numeru referencyjnego lub kodu kreskowego. Moduł obsługuje również jednostki miary oraz listy cen, umożliwiając tworzenie pełnych zamówień z jednego pliku CSV.

W przypadku gdy dane w pliku CSV są niekompletne lub niewłaściwe, moduł zawiera funkcjonalność obsługi błędów. Każdy wiersz, który nie może być poprawnie zaimportowany, jest rejestrowany i prezentowany użytkownikowi po zakończeniu procesu importu. Dzięki temu użytkownik ma pełną kontrolę nad procesem importu i łatwo może zidentyfikować i poprawić błędne dane.

Na koniec procesu importu, moduł wyświetla powiadomienie o sukcesie, zawierające liczbę zaimportowanych rekordów oraz liczby pominiętych lub błędnych wierszy. Umożliwia to użytkownikowi łatwe monitorowanie efektywności i dokładności procesu importu.


<h3>ENG</h3>

The Import Order module developed for Odoo aims to provide an efficient solution for importing sales orders from CSV files into the system. The module is designed with numerous features that ensure smooth and seamless order import, while addressing potential exceptions.

Upon loading a CSV file, the module processes each line individually, attempting to create a new sales order for each unique sales order reference in the file. It manages the association of products and customers (individuals or companies) with respective sales orders. The module searches for products and customers within the system, but it can also create new records when needed. The system handles validation for each SO and its corresponding order lines, ensuring that required data for each product, such as the unit of measure and unit price, are correctly imported.

The module includes functionality to create or identify addresses associated with customers, both for invoicing and delivery. It first searches the existing address records and, if none matches, creates new addresses accordingly.

Furthermore, the module handles errors and exceptions in a user-friendly way. If an error occurs during import (e.g., missing or incorrect data), the line number along with the specific error message is recorded and presented to the user in a comprehensive summary at the end of the import process. It also confirms the successful creation of sales orders, notifying the user of how many records have been successfully imported.
