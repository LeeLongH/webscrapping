from airflow.utils.email import send_email

def compose_email(**kwargs):
    ti = kwargs['ti']
    subject = "Webscraping DAG Report"
    
    # Check if scraping succeeded
    task_instance = kwargs['task_instance']
    scraping_task_state = task_instance.xcom_pull(task_ids='webscrapping', key='return_value')
    scraping_task_status = kwargs['dag_run'].get_task_instance('webscrapping').state

    # If the scraping task failed
    if scraping_task_status != 'success':
        html_content = f"""
        <h3>❌ Webscraping DAG failed!</h3>
        <p>Task <b>webscrapping</b> ended with state: <b>{scraping_task_status}</b></p>
        <p>Check Airflow logs for more details.</p>
        """
    else:
        # If success, include jobs data
        if scraping_task_state is None or not scraping_task_state.get("jobs"):
            html_content = "<h3>No jobs found for today.</h3>"
        else:
            html_content = "<h3>✅ Webscraping succeeded! Today's Jobs:</h3>"
            for job in scraping_task_state["jobs"]:
                html_content += f"""
                <p>
                    <b>Title:</b> {job.get('title', 'No title')}<br>
                    <b>Location:</b> {job.get('location', 'No location')}<br>
                    <b>Description:</b> {job.get('description', 'No description')}<br>
                    <b>URI:</b> <a href="{job.get('uri', 'No link')}">{job.get('uri', 'No link')}</a>
                </p>
                <hr>
                """
    
    send_email(
        to=['leon.sturm2@gmail.com'],
        subject=subject,
        html_content=html_content
    )
