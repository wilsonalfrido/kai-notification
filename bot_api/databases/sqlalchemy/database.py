import pandas as pd
import traceback
import time
from typing import Any, List, TypeVar, Union
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Any, List, TypeVar, Union, Dict
import logging
from databases.sqlalchemy.models import Base
from functools import wraps
from sqlite3 import OperationalError

from source.logger import create_logger

GENERIC = TypeVar("GENERIC")


class Database:
    def __init__(self, DB_ENGINE) -> None:
        self.engine = DB_ENGINE
        self.session = sessionmaker(bind=DB_ENGINE)()
        self.logger = create_logger(__name__)

    def retry(max_retries=5, retry_interval=5):
        """
        A decorator for retrying a function with a specified number of retries and interval.

        Parameters:
        - max_retries (int): The maximum number of retry attempts (default is 5).
        - retry_interval (int): The time in seconds to wait between retry attempts (default is 5 seconds).
        """

        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                for retry_attempt in range(1, max_retries + 1):
                    try:
                        result = func(self, *args, **kwargs)
                        return result  # Successful execution, exit the loop
                    except Exception as err:
                        self.session.rollback()
                        self.logger.error(f"Error: {str(err)}")

                        if retry_attempt < max_retries:
                            self.logger.info(
                                f"Retrying in {retry_interval} seconds (Attempt {retry_attempt}/{max_retries})"
                            )
                            time.sleep(retry_interval)
                        else:
                            if isinstance(err, OperationalError):
                                self.logger.error(f"Failed to connect to DB!")
                            else:
                                self.logger.error(
                                    f"Failed executing the operation to the database!"
                                )
                            self.logger.error(traceback.format_exc())
                            raise err  # Maximum retries reached, raise the exception
                    finally:
                        self._flush_session()

            return wrapper

        return decorator

    def _flush_session(self) -> None:
        self.session.flush()

    @retry(max_retries=3,retry_interval=3)
    def insert(self, data: Union[List[Base], Base]) -> Union[List[Base], Base]:
        try:
            is_list = isinstance(data, list)

            if is_list:
                self.session.add_all(data)
            else:
                self.session.add(data)

            self.session.commit()
            self.logger.info(f"Successfully inserted the data!")
        
        except Exception as e:
            self.logger.error(f"Failed inserting the data to database!")
            self.logger.error(traceback.format_exc())
            self.logger.error(e)
            raise Exception(f'Failed inserting the data to database! -> {e}')
        
        finally:
            self._flush_session()

    @retry(max_retries=3,retry_interval=3)
    def read(self, target: GENERIC, filters: Any = None) -> pd.DataFrame:
        try:
            if isinstance(target, list):
                query = self.session.query(*target)
            else:
                query = self.session.query(target)

            if filters:
                if type(filters) != list:
                    query = query.filter(filters)
                else:
                    for filter in filters:
                        query = query.filter(filter)
            return pd.read_sql(query.statement, query.session.bind)
        except Exception as e:
            self.logger.error(f"Failed getting the data from database!")
            self.logger.error(traceback.format_exc())
            self.logger.error(e)
            raise Exception(f'Failed getting the data from database -> {e}')

        finally:
            self._flush_session()
    
    @retry()
    def update(self, target: GENERIC, id: str, updates: Dict[str, Any]) -> bool:
        try:
            self.logger.info(
                f"Beginning update on row with ID {id} from table {target.__tablename__}"
            )
            target_attribute = getattr(target, "id")
            id_filter = target_attribute == id

            self.session.query(target).filter(id_filter).update(updates)
            self.session.commit()

            self.logger.info(f"Successfully updated row with ID {id}")
            return True
        except Exception as err:
            self.logger.error(f"Failed reading the data from database!")
            self.logger.error(traceback.format_exc())
            self.logger.error(err)

            return False
        finally:
            self._flush_session()

        


