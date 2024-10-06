export const HealthTalk = () => {
    return (
        <div className="p-3">
            <h2>Health Talk</h2>
            <p>Health Talk Placeholder</p>
            {data ? (
                <div>
                    <div>Id: {data.id}</div>
                    <div>Value: {data.value}</div>
                </div>
            ):{
                <div>Loading...</div>
            }}
        </div>
    );
};